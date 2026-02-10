from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

app = APIRouter(prefix='/users', tags=['users'])


@app.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
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
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    users = session.scalars(select(User).offset(offset).limit(limit))
    return {'users': users}


@app.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
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

        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already registered',
        )


@app.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()
    return Message(message='User deleted successfully')
