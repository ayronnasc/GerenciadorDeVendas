from http import HTTPStatus


def test_root(client):

    response = client.get('/')

    assert response.json() == {'message': 'ola mundo!'}
    assert response.status_code == HTTPStatus.OK
