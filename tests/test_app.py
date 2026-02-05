from http import HTTPStatus


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


def test_read_users_must_return_list_of_users(client):
    for _ in range(1):
        client.post(
            '/users/',
            json={
                'username': 'joao',
                'email': 'joao@example.com',
                'password': 'senha',
            },
        )
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'joao',
                'email': 'joao@example.com',
                'id': 1,
            },
            {
                'username': 'joao',
                'email': 'joao@example.com',
                'id': 2,
            },
        ]
    }


def test_update_user_must_return_updated_user(client):
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


def test_delete_user_must_return_204_no_content(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_must_return_404_if_user_not_found(client):
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
