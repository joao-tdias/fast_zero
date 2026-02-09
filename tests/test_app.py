from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root_must_return_hello_world(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_read_root_must_return_hello_world_html(client):
    response = client.get('/html')
    assert response.status_code == HTTPStatus.OK
    assert (
        response.content
        == b"""
    <html>
        <head>
            <title>First Hello World!</title>
        </head>
        <body>
            <h1>Hello World!</h1>
        </body>
    </html>"""
    )


def test_create_user_must_return_user_with_id(client):
    response = client.post(
        '/users/',
        json={
            'username': 'joao',
            'email': 'joao@example.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'joao',
        'email': 'joao@example.com',
        'id': 1,
    }


def test_create_user_must_return_409_if_username_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'joao',
            'email': 'joao2@example.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already registered'}


def test_create_user_must_return_409_if_email_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'joao2',
            'email': 'joao@example.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_read_users_must_return_list_of_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_must_return_list_of_users_with_user_fixture(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user_must_return_updated_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'joao_updated',
            'email': 'joao_updated@example.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'joao_updated',
        'email': 'joao_updated@example.com',
        'id': 1,
    }


def test_update_user_must_return_404_if_user_not_found(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'non_existent',
            'email': 'non_existent@example.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_integrity_error(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'another_user',
            'email': 'another_user@example.com',
            'password': 'senha',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'another_user',
            'email': 'change@example.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already registered'
    }


def test_delete_user_must_return_204_no_content(client, user):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_must_return_404_if_user_not_found(client):
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
