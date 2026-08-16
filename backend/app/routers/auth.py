from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas.application import Token
from app.security import get_current_user
from app.services.auth import S_refresh_token, get_token, revoke_jti, decode_no_exceptions

router = APIRouter(prefix='/auth', tags=['auth'])



Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    response: Response,
    session: Session,
    form_data: OAuth2Form,
    access_token: Annotated[str | None, Cookie()] = None,
):

    return await get_token(response, session, form_data, access_token)


@router.post('/refresh_token', response_model=Token)
async def refresh_token(
    response: Response,
    session: Session,
    refresh_token: Annotated[str | None, Cookie()] = None,
):

    if not refresh_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Refresh token invalid'
        )

    return await S_refresh_token(session, refresh_token)


@router.post('/logout')
async def logout(
    response: Response, 
    user: CurrentUser,
    refresh_token: Annotated[str | None, Cookie()] = None,
    ):
    if refresh_token:
        payload = decode_no_exceptions(refresh_token)
        if payload:
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and isinstance(exp, int):
                revoke_jti(jti, exp)

    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')
        
    return {'message': 'Logout realized with success!'}
