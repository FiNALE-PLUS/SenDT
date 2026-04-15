
from typing import Annotated

from fastapi import APIRouter, Security
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from sqlmodel import or_, select

from api.dependencies.auth.authentication import authorise_current_redacted_user
from api.utils.auth.scopes.fields import DBDeleteSubScope, DBReadSubScope, DBWriteSubScope
from api.utils.auth.scopes.scope_manager import ScopeManager, SongScopeField
from db.models.songs_and_charts import Song
from db.models.users import User
from db.session.session import AsyncSessionDep


song_router = APIRouter(prefix='/song', tags=['Songs'])

song_read_scopes = ScopeManager(song_access=SongScopeField(read_access=DBReadSubScope(granted=True))).get_scope_array()
song_write_scopes = ScopeManager(song_access=SongScopeField(write_access=DBWriteSubScope(granted=True))).get_scope_array()
song_delete_scopes = ScopeManager(song_access=SongScopeField(delete_access=DBDeleteSubScope(granted=True))).get_scope_array()

# TODO: Add more query params
@song_router.get("/")
async def get_song_page(
    current_user: Annotated[User, Security(authorise_current_redacted_user, scopes=song_read_scopes)],
    session: AsyncSessionDep,
    name:   str | None = None,
    artist_id: int | None = None
) -> Page[Song]:
    song_query = select(Song)
    if name:
        song_query = song_query.where(or_(Song.name_en.contains(name), Song.name_jp.contains(name)))
    if artist_id:
        song_query = song_query.where(Song.artist_id == artist_id)
    
    return await apaginate(session, song_query)

@song_router.post("/")
async def add_song(
    current_user: Annotated[User, Security(authorise_current_redacted_user, scopes=song_write_scopes)],
    song: Song
):
    ...