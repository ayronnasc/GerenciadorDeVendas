from datetime import datetime
from http import HTTPStatus

import factory
import pytest

from app.models import Sale


class SaleFactory(factory.Factory):
    class Meta:
        model = Sale

    description = factory.Faker('text')
    total = 0.0
    user_id = 1

    @factory.post_generation
    def items(self: Sale, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for item in extracted:
                amount = kwargs.get('amount', 1)

                self.add_item(item=item, amount=amount, value=item.value)


def test_create_sale(client, token, mock_db_time, items):

    EXP_AMOUNT = 1

    previous_amount = items[0].amount

    with mock_db_time(model=Sale) as time:
        response = client.post(
            '/sales/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'description': 'Test Sale Description',
                'items': [
                    {
                        'item_id': items[0].id,
                        'amount': EXP_AMOUNT,
                    }
                ],
            },
        )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'description': 'Test Sale Description',
        'items': [
            {
                'amount': 1,
                'value': items[0].value,
                'item': {
                    'id': items[0].id,
                    'title': items[0].title,
                    'description': items[0].description,
                    'amount': items[0].amount,
                    'value': items[0].value,
                    'state': 'available',
                    'created_at': items[0].created_at.isoformat(),
                    'updated_at': items[0].updated_at.isoformat(),
                },
            }
        ],
        'id': 1,
        'total': items[0].value * EXP_AMOUNT,
        'created_at': f'{time[0].isoformat()}',
        'updated_at': f'{time[1].isoformat()}',
    }

    assert response.json()['items'][0]['item']
    ['amount'] == previous_amount + EXP_AMOUNT


@pytest.mark.asyncio
async def test_list_sales_should_return_5_sales(
    session, client, user, token, items
):
    # arrange
    expected_sales = 5
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            items=[items[0], items[1]],
        )
    )
    await session.commit()

    # act
    response = client.get(
        '/sales/',
        headers={'Authorization': f'Bearer {token}'},
    )

    # assert
    assert len(response.json()['sales']) == expected_sales


@pytest.mark.asyncio
async def test_list_sales_pagination_should_return_2_sales(
    client, user, session, token, items
):

    expected_sales = 2
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            items=[items[0], items[1]],
        )
    )
    await session.commit()

    response = client.get(
        '/sales/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['sales']) == expected_sales


@pytest.mark.asyncio
async def test_list_sales_filter_description_should_return_5_sales(
    client, user, session, token, items
):

    expected_sales = 5
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            description='Test Sale 1',
            items=[items[0], items[1]],
        )
    )
    session.add_all(SaleFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/sales/?description=Test Sale 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    list = response.json()['sales']

    for item in list:
        assert item['description'] == 'Test Sale 1'
    assert len(response.json()['sales']) == expected_sales


@pytest.mark.asyncio
async def test_list_sales_filter_total_should_return_5_sales(
    client, user, session, token, items
):

    expected_sales = 5
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            description='Test Sale 1',
            items=[items[0], items[1]],
        )
    )
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            items=[items[2], items[3]],
        )
    )
    await session.commit()

    expected_total = (items[0].value * 1) + (items[1].value * 1)
    response = client.get(
        f'/sales/?total={expected_total}',
        headers={'Authorization': f'Bearer {token}'},
    )

    list = response.json()['sales']

    for sale in list:
        assert sale['total'] == expected_total
    assert len(response.json()['sales']) == expected_sales


@pytest.mark.asyncio
async def test_list_sales_filter_greaterthan_should_return_5_sales(
    client, user, session, token, items
):

    expected_sales = 5
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            description='Test Sale 1',
            items=[items[0], items[1]],
        )
    )
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
        )
    )
    await session.commit()

    expected_greater = 1
    response = client.get(
        f'/sales/?greater_than={expected_greater}',
        headers={'Authorization': f'Bearer {token}'},
    )

    list = response.json()['sales']

    for sale in list:
        assert sale['total'] > expected_greater
    assert len(response.json()['sales']) == expected_sales


@pytest.mark.asyncio
async def test_list_sales_filter_lessthan_should_return_5_sales(
    client, user, session, token, items
):

    expected_sales = 5
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            description='Test Sale 1',
            items=[items[0], items[1]],
        )
    )
    session.add_all(
        SaleFactory.create_batch(
            5,
            user_id=user.id,
            items=[items[2], items[3]],
            items__amount=100,
        )
    )
    await session.commit()

    expected_less = 100
    response = client.get(
        f'/sales/?less_than={expected_less}',
        headers={'Authorization': f'Bearer {token}'},
    )

    list = response.json()['sales']

    for sale in list:
        assert sale['total'] < expected_less
    assert len(response.json()['sales']) == expected_sales


@pytest.mark.asyncio
async def test_delete_sale(client, user, session, token, items):

    sale = SaleFactory(user_id=user.id, items=[items[0], items[1]])

    session.add(sale)
    await session.commit()

    response = client.delete(
        f'/sales/{sale.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Sale deleted with success!'}


@pytest.mark.asyncio
async def test_delete_sale_error(client, token):
    response = client.delete(
        '/sales/10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Sale not found'}


@pytest.mark.asyncio
async def test_delete_sale_other_user_error(
    client, user, other_user, session, token, items
):

    sale_other_user = SaleFactory(
        user_id=other_user.id, items=[items[0], items[1]]
    )
    session.add(sale_other_user)
    await session.commit()

    response = client.delete(
        f'/sales/{sale_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Sale not found'}


@pytest.mark.asyncio
async def test_patch_sale_error(client, token):
    response = client.patch(
        '/sales/10', json={}, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Sale not found'}


@pytest.mark.asyncio
async def test_patch_sale(client, token, session, user, mock_db_time, items):
    sale = SaleFactory(user_id=user.id, items=[items[0], items[1]])

    with mock_db_time(model=Sale, time=datetime(2026, 7, 21)) as time:
        sale.created_at = f'{time[0].isoformat()}'
        sale.updated_at = f'{time[1].isoformat()}'

        session.add(sale)

        await session.commit()
        await session.refresh(sale)

        response = client.patch(
            f'/sales/{sale.id}',
            json={
                'description': 'teste!',
                'items': [{'item_id': items[0].id, 'amount': 2}],
            },
            headers={'Authorization': f'Bearer {token}'},
        )

        expected_total = (items[0].value * 2) + items[1].value

        assert response.status_code == HTTPStatus.OK
        assert response.json()['sale']['description'] == 'teste!'

        assert response.json()['sale']['items'] == [
            {
                'amount': 1,
                'value': items[1].value,
                'item': {
                    'id': items[1].id,
                    'title': items[1].title,
                    'description': items[1].description,
                    'amount': items[1].amount,
                    'value': items[1].value,
                    'state': 'available',
                    'created_at': items[1].created_at.isoformat(),
                    'updated_at': items[1].updated_at.isoformat(),
                },
            },
            {
                'amount': 2,
                'value': items[0].value,
                'item': {
                    'id': items[0].id,
                    'title': items[0].title,
                    'description': items[0].description,
                    'amount': items[0].amount,
                    'value': items[0].value,
                    'state': 'available',
                    'created_at': items[0].created_at.isoformat(),
                    'updated_at': items[0].updated_at.isoformat(),
                },
            },
        ]

        assert response.json()['sale']['total'] == expected_total

        assert response.json()['sale']
        ['created_at'] == sale.created_at.isoformat()
        assert response.json()['sale']['updated_at'] != time[1].isoformat()
