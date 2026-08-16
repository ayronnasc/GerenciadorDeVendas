from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated, Optional
from zoneinfo import ZoneInfo
import time

from uuid import UUID, uuid4

import jwt

from fastapi import Depends, HTTPException, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.User import User
from app.settings import Settings

from app.services.redis import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

pwd_context = PasswordHash.recommended()

settings = Settings()

Session = Annotated[AsyncSession, Depends(get_session)]


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def is_revoked(jti) -> bool:
    if not jti:
            return False
    return redis_client.exists(f"jwt:blacklist:{jti}") == 1

async def verify_token_origin(session, token):

    credencials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    if not token:
        return False

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        jti = payload.get("jti")
        if is_revoked(jti):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token revoked")

        subject_email = payload.get('sub')

        exp = payload.get("exp")
        if exp is None:
            raise credencials_exception

        if exp <= int(time.time()):
            raise credencials_exception

        if not subject_email:
            raise credencials_exception

        return await session.scalar(select(User).where(User.email == subject_email))
    except DecodeError:
        raise credencials_exception
    except ExpiredSignatureError:
        raise credencials_exception

def create_access_from_refresh_token(token):
    credencials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    if not token:
        return False

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        subject_email = payload.get('sub')
        user_id = payload.get('id')

        if not subject_email:
            raise credencials_exception

        new_token = create_access_token({
            'sub': subject_email,
            'id': user_id,
            'jti': str(uuid4())
        })

        return new_token
        
    except DecodeError:
        raise credencials_exception
    except ExpiredSignatureError:
        raise credencials_exception

def create_access_token(data: dict) -> str:

    to_encode = data.copy()
    to_encode.update({'jti': str(uuid4())})

    expire = int(time.time()) + 9000
    to_encode.update({'exp': expire})

    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def create_refresh_token(data: dict) -> str:

    to_encode = data.copy()
    to_encode.update({'jti': str(uuid4())})

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(days=7)
    to_encode.update({'exp': expire})

    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt



async def get_current_user(
    session: Session,
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    print(f"Cookies recebidos: {request.cookies}")

    credencials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    if not access_token:
        raise credencials_exception

    try:
        payload = decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        jti = payload.get("jti")
        if is_revoked(jti):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token revoked")
        
        subject_email = payload.get('sub')
        if not subject_email:
            raise credencials_exception
    except DecodeError:
        raise credencials_exception
    except ExpiredSignatureError:
        raise credencials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        raise credencials_exception

    return user
