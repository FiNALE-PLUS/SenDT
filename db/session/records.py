from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.models.users import UserAccess
from db.session.session import async_engine


async def configure_default_db_enums():
    # Avoids requiring working with an async generator, which throws a lot of errors without prerequisite knowledge
    async with AsyncSession(async_engine) as session:
        await configure_access_levels_without_commit(session)
        # await session.commit()


async def configure_access_levels_without_commit(session: AsyncSession):
    required_access_levels = (
        UserAccess(id=1, name='none'),
        UserAccess(id=2, name='viewer'),
        UserAccess(id=3, name='dev'),
        UserAccess(id=4, name='admin')
    )

    for access_level in required_access_levels:
        try:
            selection = (await session.exec(select(UserAccess).where(UserAccess.id == access_level.id))).one()
        except NoResultFound:
            session.add(access_level)
            
    await session.commit()
