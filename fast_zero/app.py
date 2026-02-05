from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get('/', status_code=200)
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
