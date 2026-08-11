from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.User import User
from app.schemas.application import Token
from app.security import get_current_user
from app.services.auth import S_refresh_token, get_token

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
async def login_for_acess_token(
    session: Session,
    form_data: OAuth2Form,
):
    return await get_token(session, form_data)


@router.post('/refresh_token', response_model=Token)
async def refresh_token(user: Annotated[User, Depends(get_current_user)]):
    return await S_refresh_token(user)
