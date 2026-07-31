from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Item_Sale import Item_Sale
from app.models.Sale import Sale
from app.models.User import User
from app.schemas.sale import SalePublic, SaleSchema
from app.security import get_current_user, get_session

router = APIRouter(prefix='/sales', tags=['sales'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=SalePublic, status_code=HTTPStatus.CREATED)
async def create_sale(sale: SaleSchema, session: Session, user: CurrentUser):
    db_sale = Sale(
        description=sale.description,
        user_id=user.id,
    )

    session.add(db_sale)
    await session.commit()
    db_sale = await session.refresh(db_sale)

    for item in db_sale.items:
        session.add(
            Item_Sale(
                sale_id=item.sale_id,
                item_id=item.item_id,
                user_id=user.id,
                amount=item.amount,
                value=item.value,
            )
        )
    await session.commit()

    db_sale = await session.refresh(db_sale)

    return db_sale
