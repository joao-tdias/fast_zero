from dataclasses import asdict

from sqlalchemy import select

from fast_zero import database
from fast_zero.models import User


def test_create_user(session, mock_db_time):

    with mock_db_time(model=User) as time:
        new_user = User(
            username='testuser',
            email='testuser@example.com',
            password='password',
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'testuser'))

    assert asdict(user) == {
        'id': 1,
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password',
        'created_at': time,
        'updated_at': time,
    }


def test_get_session(session):
    # ensure get_session yields a Session bound to the same engine used by the
    # test `session` fixture and that operations are visible across sessions

    # Replace the engine used by the module with the in-memory engine from
    # the fixture so get_session will create sessions against the test DB.
    database.engine = session.get_bind()

    gen = database.get_session()
    new_session = next(gen)

    # basic sanity: it's a Session bound to the same engine
    assert new_session.get_bind() is session.get_bind()

    user = User(username='other', email='other@example.com', password='pwd')
    new_session.add(user)
    new_session.commit()

    queried = session.scalar(select(User).where(User.username == 'other'))
    assert queried is not None
    assert queried.username == 'other'

    gen.close()
