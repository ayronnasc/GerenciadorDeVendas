from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item, User
from app.schemas.item import ItemSchema


async def add_item(item: ItemSchema, session: AsyncSession, user: User):

    db_item = Item(
        title=item.title,
        description=item.description,
        value=item.value,
        amount=item.amount,
        state=item.state,
        user_id=user.id,
    )

    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return db_item
