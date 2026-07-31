from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
    )

    session.add(db_sale)
    await session.commit()
    await session.refresh(db_sale)

    for item_sale in sale.items:
        item = await session.scalar(select(Item).where(Item.id == item_sale.item_id))
        
        if not item:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Item not found - Loop error"
            )

        if item.state != ItemState.available:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="This item is not available for sale"
            )
        
        if item.amount < 0:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="This item is sold out"
            )

        if item.amount < item_sale.amount:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="The amount you required is not available for this item"
            )

        session.add(
            Item_Sale(
                sale_id = db_sale.id,
                item_id = item_sale.item_id,
                user_id = user.id,
                amount = item_sale.amount,
                value = item.value * item_sale.amount,
            )
        )

        item.amount = item.amount - item_sale.amount
        session.add(item)
        await session.commit()

        total += item.value * item_sale.amount

    db_sale.total = total

    session.add(db_sale)

    await session.commit()
    await session.refresh(db_sale)

    return db_sale
