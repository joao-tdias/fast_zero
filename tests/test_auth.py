from http import HTTPStatus

from freezegun import freeze_time


def test_login(client, user):
    response = client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_login_invalid_credentials(client, user):
    response = client.post(
        '/auth/login',
        data={'username': user.email, 'password': 'wrongpassword'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid credentials'}


def test_token_expiration(client, user):
    with freeze_time('2025-01-01 00:00:00'):
        response = client.post(
            '/auth/login',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']
    with freeze_time('2025-01-01 00:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'newusername',
                'email': 'change@example.com',
                'password': 'newpassword',
            },
        )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token(client, user, token):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'


def test_token_expired_doesnt_refresh(client, token, user):
    with freeze_time('2025-01-01 01:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
    with freeze_time('2025-01-01 01:31:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Token has expired'}
