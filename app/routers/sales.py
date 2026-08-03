from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import select
from app.models import Item_Sale
from app.models import Item
from app.models.Item import ItemState
from app.models import Sale
from app.models import User
from app.schemas.sale import SalePublic, SaleSchema
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

        total += _item.value * item.amount
        db_sale.items.append(Item_Sale(amount=item.amount, value=_item.value, items=_item))

    db_sale.total = total

    session.add(db_sale)
    await session.commit()
    await session.refresh(db_sale)

    return db_sale


@router.get('/{sale_id}', status_code=HTTPStatus.CREATED)
async def create_sale(sale_id: int, session: Session, user: CurrentUser):

    db_sale = await session.scalar(select(Sale).where(Sale.user_id == user.id, Sale.id == sale_id).options(selectinload(Sale.items)))
    for assoc in db_sale.items:
        print(assoc.amount)
        print(assoc.value)
        print(assoc.items)

    breakpoint()
    
    return db_sale
