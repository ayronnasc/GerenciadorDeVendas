from http import HTTPStatus

import pytest
from backend.app.security import create_access_token, get_current_user
from fastapi import HTTPException
from jwt import decode, encode


def test_jwt(settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


@pytest.mark.asyncio
async def test_not_subject_email_exists(session, settings, user, client):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    decoded = decode(
        response.json()['access_token'],
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM,
    )

    decoded.pop('sub')

    encoded_jwt = encode(
        decoded, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session, encoded_jwt)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'
    assert not decoded.get('sub')


@pytest.mark.asyncio
async def test_not_user_exists(session, settings, user, client):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    decoded = decode(
        response.json()['access_token'],
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM,
    )

    decoded['sub'] = 'notInDatabase@example.com'

    encoded_jwt = encode(
        decoded, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session, encoded_jwt)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
