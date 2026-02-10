from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.routes import auth, users
from fast_zero.schemas import Message

app = FastAPI()
app.include_router(auth.app)
app.include_router(users.app)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.get('/html', response_class=HTMLResponse)
def read_root_html():
    return b"""
    <html>
        <head>
            <title>First Hello World!</title>
        </head>
        <body>
            <h1>Hello World!</h1>
        </body>
    </html>"""
