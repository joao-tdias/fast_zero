from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    limit: int = Field(default=100, ge=0)
    offset: int = Field(default=0, ge=0)


# Exemplo de como evoluir com o filtro de nome, caso seja necessário
# class FilterName(FilterPage):
#     name: str = Field(default='', min_length=1)
