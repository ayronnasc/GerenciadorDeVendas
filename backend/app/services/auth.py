from http import HTTPStatus

from fastapi import HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import time

import jwt

from app.settings import Settings as settings

from app.services.redis import redis_client

from app.models import User
from app.security import (
    create_access_token,
    verify_password,
    verify_token_origin,
    create_refresh_token,
    create_access_from_refresh_token
)

ACCESS_COOKIE_EXPIRE_TIME = 9000 # 15 min

REFRESH_COOKIE_EXPIRE_TIME = (7 * 24 * 3600) + (1 * 1800)



async def get_token(
    response: Response,
    session: AsyncSession,
    form_data,
    access_token,
):      

    if access_token:
        user = await verify_token_origin(session, access_token)
        if user: 
            return {'access_token': access_token, 'token_type': 'Bearer'}
    
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorret email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorret email or password',
        )

    access_token = create_access_token({
        'sub': user.email,
        'id': str(user.id),
    })

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=ACCESS_COOKIE_EXPIRE_TIME,
    )

    refresh_token = create_refresh_token({
        'sub': user.email,
        'id': str(user.id),
    })

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=REFRESH_COOKIE_EXPIRE_TIME,
    )

    return {'access_token': access_token, 'token_type': 'Bearer'}


async def S_refresh_token(session, refresh_token):

    user_cookie = await verify_token_origin(session, refresh_token)

    if not user_cookie:
        return False
    
    token = create_access_from_refresh_token(
        token={'sub': user_cookie.email, 'id': str(user_cookie.id)}
    )

    return {'access_token': token, 'token_type': 'Bearer'}


def revoke_jti(jti: str, exp_epoch: int, now: int | None = None):
    now = now or int(time.time())
    ttl = exp_epoch - now
    if ttl > 0:
        redis_client.setex(f"jwt:blacklist:{jti}", ttl, "revoked")

def decode_no_exceptions(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        return None