import random
from datetime import datetime
from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from app.models import Item
from app.models.Item import ItemState


class ItemFactory(factory.Factory):
    class Meta:
        model = Item

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(ItemState)
    amount = factory.LazyFunction(lambda: random.randint(1, 40))
    value = factory.LazyFunction(lambda: round(random.uniform(1.0, 30.0), 2))
    user_id = 1


def test_create_item(client, token, mock_db_time):

    with mock_db_time(model=Item) as time:
        response = client.post(
            '/items/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Item',
                'description': 'Test Item Description',
                'amount': 20,
                'value': 10.0,
                'state': 'available',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'Test Item',
        'description': 'Test Item Description',
        'amount': 20,
        'value': 10.0,
        'state': 'available',
        'created_at': f'{time[0].isoformat()}',
        'updated_at': f'{time[1].isoformat()}',
    }


@pytest.mark.asyncio
async def test_list_items_should_return_5_items(session, client, user, token):
    # arrange
    expected_items = 5
    session.add_all(ItemFactory.create_batch(5, user_id=user.id))
    await session.commit()

    # act
    response = client.get(
        '/items/',
        headers={'Authorization': f'Bearer {token}'},
    )

    # assert
    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_list_items_pagination_should_return_2_items(
    client, user, session, token
):

    expected_items = 2
    session.add_all(ItemFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/items/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_list_items_filter_title_should_return_5_items(
    client, user, session, token
):

    expected_items = 5
    session.add_all(
        ItemFactory.create_batch(5, user_id=user.id, title='Test Item 1')
    )
    session.add_all(ItemFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/items/?title=Test Item 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    list = response.json()['items']

    for item in list:
        assert item['title'] == 'Test Item 1'
    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_list_items_filter_description_should_return_5_items(
    client, user, session, token
):

    expected_items = 5
    session.add_all(
        ItemFactory.create_batch(
            5, user_id=user.id, description='description1'
        )
    )
    session.add_all(ItemFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/items/?description=description1',
        headers={'Authorization': f'Bearer {token}'},
    )
    list = response.json()['items']

    for item in list:
        assert item['description'] == 'description1'
    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_list_items_filter_state_should_return_5_items(
    client, user, session, token
):
    expected_items = 5
    session.add_all(
        ItemFactory.create_batch(5, user_id=user.id, state=ItemState.available)
    )
    session.add_all(
        ItemFactory.create_batch(5, user_id=user.id, state=ItemState.trash)
    )

    await session.commit()

    response = client.get(
        '/items/?state=available',
        headers={'Authorization': f'Bearer {token}'},
    )

    list = response.json()['items']

    for item in list:
        assert item['state'] == ItemState.available
    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_list_items_filter_10_amount_should_return_5_items(
    client, user, session, token
):
    EXPECTED_AMOUNT = 10
    expected_items = 5

    session.add_all(ItemFactory.create_batch(5, user_id=user.id, amount=10))

    session.add_all(ItemFactory.create_batch(5, user_id=user.id, amount=5))
    await session.commit()

    response = client.get(
        '/items/?amount=10',
        headers={'Authorization': f'Bearer {token}'},
    )
    list = response.json()['items']

    for item in list:
        assert item['amount'] == EXPECTED_AMOUNT
    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_list_items_filter_3075_value_should_return_5_items(
    client, user, session, token
):
    EXPECTED_VALUE = 30.75
    expected_items = 5

    session.add_all(
        ItemFactory.create_batch(5, user_id=user.id, value=EXPECTED_VALUE)
    )

    session.add_all(ItemFactory.create_batch(5, user_id=user.id, value=5.80))
    await session.commit()

    response = client.get(
        f'/items/?value={EXPECTED_VALUE}',
        headers={'Authorization': f'Bearer {token}'},
    )
    list = response.json()['items']

    for item in list:
        assert item['value'] == EXPECTED_VALUE
    assert len(response.json()['items']) == expected_items


@pytest.mark.asyncio
async def test_delete_item(client, user, session, token):

    item = ItemFactory(user_id=user.id)

    session.add(item)
    await session.commit()

    response = client.delete(
        f'/items/{item.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Item has been deleted sucessfully'}


@pytest.mark.asyncio
async def test_delete_item_error(client, token):
    response = client.delete(
        '/items/10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}


@pytest.mark.asyncio
async def test_delete_item_other_user_error(
    client, other_user, session, token
):

    item_other_user = ItemFactory(user_id=other_user.id)
    session.add(item_other_user)
    await session.commit()

    response = client.delete(
        f'/items/{item_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}


@pytest.mark.asyncio
async def test_patch_item_error(client, token):
    response = client.patch(
        '/items/10', json={}, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}


@pytest.mark.asyncio
async def test_patch_item(client, token, session, user, mock_db_time):
    item = ItemFactory(user_id=user.id)

    with mock_db_time(model=Item, time=datetime(2026, 7, 21)) as time:
        item.created_at = f'{time[0].isoformat()}'
        item.updated_at = f'{time[1].isoformat()}'
        session.add(item)
        await session.commit()
        await session.refresh(item)

        response = client.patch(
            f'/items/{item.id}',
            json={'title': 'teste!'},
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json()['title'] == 'teste!'
        assert response.json()['created_at'] == item.created_at.isoformat(
            timespec='seconds'
        )
        assert response.json()['updated_at'] != time[1].isoformat(
            timespec='seconds'
        )
