from http import HTTPStatus

import factory.fuzzy
import pytest

from fast_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text', max_nb_chars=20)
    description = factory.Faker('text', max_nb_chars=100)
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, user, token):
    response = client.post(
        '/todos/',
        json={
            'title': 'Test Todo',
            'description': 'This is a test todo',
            'state': 'todo',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['title'] == 'Test Todo'
    assert data['description'] == 'This is a test todo'
    assert data['state'] == 'todo'
    assert 'id' in data


@pytest.mark.asyncio
async def test_get_todo_should_return_5_todos(client, token, session, user):
    expected_todos = 5
    session.add_all(TodoFactory.build_batch(expected_todos, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_change_todo_state(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={
            'state': 'done',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['state'] == 'done'


def test_delete_todo(client, token):
    response = client.post(
        '/todos/',
        json={
            'title': 'Test Todo',
            'description': 'This is a test todo',
            'state': 'todo',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CREATED

    todo_id = response.json()['id']
    response = client.delete(
        f'/todos/{todo_id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Todo deleted successfully'}
