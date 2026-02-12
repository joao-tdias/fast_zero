from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError
from pwdlib import PasswordHash
from sqlalchemy import select

from fast_zero.database import GetSession
from fast_zero.models import User
from fast_zero.settings import Settings

SECRET_KEY = Settings().SECRET_KEY
ALGORITHM = Settings().ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Settings().ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

Oauth2Scheme = Annotated[str, Depends(oauth2_scheme)]


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(session: GetSession, token: Oauth2Scheme) -> str:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_email: str = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )
    if not user:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
