from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from fast_zero.database import GetSession
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import (
    create_access_token,
    verify_password,
)

FormData = Annotated[OAuth2PasswordRequestForm, Depends()]


app = APIRouter(prefix='/auth', tags=['auth'])


@app.post('/login', status_code=HTTPStatus.OK, response_model=Token)
async def login(
    session: GetSession,
    form_data: FormData,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid credentials'
        )
    access_token = create_access_token({'sub': user.email})
    return Token(access_token=access_token, token_type='Bearer')
