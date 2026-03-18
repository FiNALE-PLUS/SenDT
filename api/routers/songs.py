
from typing import Annotated

from fastapi import APIRouter, Security

from api.dependencies.auth.authentication import authorise_current_user
from api.utils.auth.scopes.fields import DBDeleteSubScope, DBReadSubScope, DBWriteSubScope
from api.utils.auth.scopes.scope_manager import ScopeManager, SongScopeField
from db.models.songs_and_charts import Song
from db.models.users import User


song_router = APIRouter(prefix='/song', tags=['Songs'])

song_read_scopes = ScopeManager(song_access=SongScopeField(read_access=DBReadSubScope(granted=True))).get_scope_array()
song_write_scopes = ScopeManager(song_access=SongScopeField(write_access=DBWriteSubScope(granted=True))).get_scope_array()
song_delete_scopes = ScopeManager(song_access=SongScopeField(delete_access=DBDeleteSubScope(granted=True))).get_scope_array()

@song_router.post("/new")
async def add_song(
    current_user: Annotated[User, Security(authorise_current_user, scopes=song_write_scopes)],
    song: Song
):
    ...