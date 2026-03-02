from db.models.users import UserAccess
from db.session.session import get_session


def configure_default_db_enums():
    session = next(get_session())

    session.add(UserAccess(id=1, name='none'))
    session.add(UserAccess(id=2, name='viewer'))
    session.add(UserAccess(id=3, name='dev'))
    session.add(UserAccess(id=4, name='admin'))

    session.commit()