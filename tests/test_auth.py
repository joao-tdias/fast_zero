from http import HTTPStatus


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
