from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.application import Message
from app.schemas.filters import FilterSale
from app.schemas.sale import (
    SaleList,
    SalePublic,
    SaleResponse,
    SaleSchema,
    SaleUpdate,
)
from app.security import get_current_user, get_session
from app.services.sales import (
    S_create_sale,
    S_delete_sale,
    S_get_sales,
    S_update_sale,
)

router = APIRouter(prefix='/sales', tags=['sales'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=SalePublic, status_code=HTTPStatus.CREATED)
async def create_sale(sale: SaleSchema, session: Session, user: CurrentUser):
    return await S_create_sale(sale, session, user)


@router.get('/', status_code=HTTPStatus.OK, response_model=SaleList)
async def list_sales(
    user: CurrentUser,
    session: Session,
    sale_filter: Annotated[FilterSale, Query()],
):
    return await S_get_sales(user, session, sale_filter)


@router.patch(
    '/{sale_id}', response_model=SaleResponse, status_code=HTTPStatus.OK
)
async def update_sale(
    sale_id: int, sale: SaleUpdate, session: Session, user: CurrentUser
):
    return await S_update_sale(sale_id, sale, session, user)


@router.delete('/{sale_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_sale(sale_id: int, session: Session, user: CurrentUser):
    return await S_delete_sale(sale_id, session, user)
