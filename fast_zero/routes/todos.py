from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from fast_zero.database import GetSession
from fast_zero.models import Todo
from fast_zero.schemas import (
    FilterTodo,
    Message,
    TaskTodo,
    TaskTodoList,
    TaskTodoPublic,
    TaskTodoUpdate,
)
from fast_zero.security import CurrentUser

app = APIRouter(prefix='/todos', tags=['todos'])


@app.post(
    '/',
    status_code=HTTPStatus.CREATED,
    summary='Create a new todo',
    response_model=TaskTodoPublic,
)
async def create_todo(
    todo: TaskTodo, session: GetSession, user: CurrentUser
) -> TaskTodoPublic:
    todo_dict = todo.dict()
    todo = Todo(**todo_dict, user_id=user.id)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return TaskTodoPublic(**todo_dict, id=todo.id)


@app.get('/', summary='Get todos with filters', response_model=TaskTodoList)
async def get_todos_filtered(
    session: GetSession,
    user: CurrentUser,
    filter_todo: Annotated[FilterTodo, Query()],
) -> TaskTodoList:
    query = select(Todo).where(Todo.user_id == user.id)

    if filter_todo.title:
        query = query.where(Todo.title.contains(filter_todo.title))
    if filter_todo.description:
        query = query.where(Todo.description.contains(filter_todo.description))
    if filter_todo.state:
        query = query.where(Todo.state == filter_todo.state)

    todos = await session.scalars(
        query.offset(filter_todo.offset).limit(filter_todo.limit)
    )
    return {'todos': todos.all()}


@app.patch(
    '/{todo_id}/',
    summary='Change the state of a todo',
    response_model=TaskTodoPublic,
)
async def change_todo(
    todo_id: int,
    new_todo: TaskTodoUpdate,
    session: GetSession,
    user: CurrentUser,
) -> TaskTodoPublic:
    db_todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )
    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    for key, value in new_todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


@app.delete(
    '/{todo_id}/',
    summary='Delete a todo',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_todo(
    todo_id: int, session: GetSession, user: CurrentUser
) -> None:
    breakpoint()
    todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    await session.delete(todo)
    await session.commit()
    return Message(message='Todo deleted successfully')
