from sqlalchemy.exc import NoResultFound
from sqlmodel import select, Session

from db.models.users import UserAccess
from db.session.session import get_session


def configure_default_db_enums():
    session = next(get_session())

    configure_access_levels_without_commit(session)

    session.commit()


def configure_access_levels_without_commit(session: Session):
    required_access_levels = (
        UserAccess(id=1, name='none'),
        UserAccess(id=2, name='viewer'),
        UserAccess(id=3, name='dev'),
        UserAccess(id=4, name='admin')
    )

    for access_level in required_access_levels:
        try:
            session.exec(select(UserAccess).where(UserAccess.id == access_level.id)).one()
        except NoResultFound:
            session.add(access_level)
