from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_read_root_must_return_hello_world():
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_read_root_must_return_hello_world_html():
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
