from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import select
from app.models import Item
from app.models import Sale
from app.models import User
from app.schemas.sale import SalePublic, SaleSchema, SaleList
from app.schemas.filters import FilterSale
from app.security import get_current_user, get_session

router = APIRouter(prefix='/sales', tags=['sales'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=SalePublic, status_code=HTTPStatus.CREATED)
async def create_sale(sale: SaleSchema, session: Session, user: CurrentUser):
    
    total = 0.0

    db_sale = Sale(
        description=sale.description,
        user_id=user.id,
        total=total,
    )
    
    for item in sale.items:
        _item = await session.scalar(select(Item).where(Item.id == item.item_id))
        if not _item: 
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="the item does not exists")
        db_sale.add_item(_item, amount=item.amount, value=_item.value)
    
    session.add(db_sale)
    await session.commit()
    await session.refresh(db_sale)
    
    return db_sale

@router.get('/{sale_id}', status_code=HTTPStatus.OK, response_model=SaleList)
async def list_items(
    user: CurrentUser,
    session: Session,
    sale_filter: Annotated[FilterSale, Query()],
):
    
    query = select(Sale).where(Sale.user_id == user.id)
    
    if sale_filter.total:
        query = query.filter(Sale.total.contains(sale_filter.total))
    if sale_filter.description:
        query = query.filter(
            Sale.description.contains(sale_filter.description)
        )

    sales = await session.scalars(
        query.limit(sale_filter.limit).offset(sale_filter.offset)
    )
    
    return {'sales': sales.all()}