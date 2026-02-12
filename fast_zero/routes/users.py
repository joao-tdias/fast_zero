from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.database import GetSession
from fast_zero.models import User
from fast_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_zero.security import CurrentUser, get_password_hash

app = APIRouter(prefix='/users', tags=['users'])
Filter = Annotated[FilterPage, Query()]


@app.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: GetSession):
    db_user = await session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already registered',
            )
        elif db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already registered',
            )

    db_user = User(
        **user.model_dump(exclude='password'),
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@app.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: GetSession, current_user: CurrentUser, filter_users: Filter
) -> UserList:
    users = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    return {'users': users}


@app.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: GetSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )
    try:
        data = user.model_dump(exclude_unset=True, exclude={'password'})
        hashed_password = (
            get_password_hash(user.password) if user.password else None
        )
        for k, v in data.items():
            setattr(current_user, k, v)

        if hashed_password:
            current_user.password = hashed_password

        await session.commit()
        await session.refresh(current_user)
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already registered',
        )


@app.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(
    user_id: int,
    session: GetSession,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    await session.commit()
    return Message(message='User deleted successfully')
