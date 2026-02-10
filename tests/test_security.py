from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user,
)


def test_create_access_token():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)
    assert decoded['test'] == data['test']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalidtoken'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_current_user_key_to_token(session):
    token = create_access_token({'su': ''})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, token=token)
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'


def test_current_user_invalid_user(session):
    token = create_access_token({'sub': 'invalid@example.com'})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, token=token)
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'
