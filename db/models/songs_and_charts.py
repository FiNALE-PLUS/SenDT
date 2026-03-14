from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, CheckConstraint, event, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .blobs import SdtChartBlob
    from .utage import UtageEntry

### Chart models

# TODO: Add cascades to allow for Song ID to be editable
#  (includes chart PK etc, or otherwise change chart PK to be composite key or fully synthetic)
class ChartDifficultyLevel(SQLModel, table=True):
    __tablename__ = 'chart_difficulty_level'

    id: int                          = Field(primary_key=True)
    name: str                        = Field(nullable=False, unique=True)

    difficulty_charts: list['Chart'] = Relationship(back_populates='difficulty_level')


class ChartCreator(SQLModel, table=True):
    __tablename__ = 'chart_creator'

    id: int                       = Field(primary_key=True)
    name_en: str
    name_jp: str

    creator_charts: list['Chart'] = Relationship(back_populates='creator')


class Chart(SQLModel, table=True):
    # Require filling from backend to allow IDs to be consistent with final text_table_ex

    __table_args__ = (
        # While this does duplicate data, it prevents de-syncs and also simplifies connections to utage listings
        # PrimaryKeyConstraint('song_id', 'difficulty_level_id'),
        # ForeignKeyConstraint(),
        UniqueConstraint("song_id", "difficulty_level_id",
                         name="one_chart_per_song_difficulty"),
        # CheckConstraint(r"id = song_id || printf('%02d', difficulty_level_id)",
        #                 name="chart_id_is_concatenated_song_and_difficulty_ids"),
        CheckConstraint(r"difficulty_constant BETWEEN 0 AND 14 AND difficulty_constant = ROUND(difficulty_constant, 1)",
                        name="chart_difficulty_in_valid_range_with_max_one_dp"),
    )

    id: int | None                         = Field(primary_key=True)

    song_id: int                           = Field(foreign_key='song.id', nullable=False, ondelete='CASCADE')
    chart_song: 'Song'                     = Relationship(back_populates='song_charts')

    difficulty_level_id: int               = Field(foreign_key="chart_difficulty_level.id", nullable=False)
    difficulty_level: ChartDifficultyLevel = Relationship(back_populates='difficulty_charts')

    difficulty_constant: Decimal           = Field(decimal_places=1, le=14, ge=0)
    affects_rating: bool                   = Field(default=False)

    creator_id: int                        = Field(default=0, foreign_key="chart_creator.id")
    creator: ChartCreator                  = Relationship(back_populates="creator_charts")
    comment: str | None                    = Field(default=None)

    chart_utage_entry: 'UtageEntry'        = Relationship(back_populates='utage_chart', cascade_delete=True)

    chart_blob_id: int | None              = Field(default=None, foreign_key="sdt_chart_blob.id")
    base_chart_blob: 'SdtChartBlob'        = Relationship(back_populates='blob_base_charts')

### Song Models


class SongArtist(SQLModel, table=True):
    __tablename__ = 'song_artist'

    __table_args__ = (
        UniqueConstraint("name_en", "name_jp", name="unique_artist_name_pair"),
    )

    id: int | None             = Field(default=None, primary_key=True)
    name_en: str
    name_jp: str

    artist_songs: list['Song'] = Relationship(back_populates='artist',
                                              sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class SongGenre(SQLModel, table=True):
    __tablename__ = 'song_genre'

    id: int                   = Field(primary_key=True)
    name_en: str              = Field(nullable=False, unique=True)
    name_jp: str              = Field(nullable=False, unique=True)

    genre_songs: list['Song'] = Relationship(back_populates='genre')


class Song(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("artist_id", "name_en", "name_jp", name="unique_song_name_and_artist"),
        CheckConstraint("bpm > 0", name="bpm_is_positive")
    )

    id: int = Field(primary_key=True)

    # Denotes whether the chart is in vanilla FiNALE
    is_vanilla: bool

    song_charts: list['Chart']    = Relationship(back_populates='chart_song', cascade_delete=True)

    artist_id: int                = Field(foreign_key='song_artist.id', ondelete='RESTRICT')
    artist: 'SongArtist'          = Relationship(back_populates='artist_songs')

    genre_id: int                 = Field(foreign_key='song_genre.id', ondelete='RESTRICT')
    genre: 'SongGenre'            = Relationship(back_populates='genre_songs')

    name_en: str                  = Field(index=True)
    name_jp: str                  = Field(index=True)
    version: int
    sub_category: int
    bpm: float
    sort_id: int
    dress: bool
    darkness: bool
    miles_counted: bool
    vl: bool
    event_id: int
    play_recording_enabled: bool
    preview_start_time: float
    preview_end_time: float
    song_length_override: int    = Field(default=0)
    off_ranking: int
    ad_def: int
    re_master: int
    special_pv: bool
    challenge_track: int
    bonus: int # ?
    sort_jp_index: int
    sort_ex_index: int
    filename: str

    comment: str | None


@event.listens_for(Song, 'before_delete')
def delete_orphaned_artist_reference(mapper, connection, target: Song):
    """
    Ensures that artists with no songs are deleted from the database
    by adding an explicit ``DELETE`` for them when they have no related songs.

    :param target: The song that is to be deleted from the DB
    """
    # after_flush used for consistent results
    @event.listens_for(Session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        # Check if the Song's artist has any remaining songs
        if target.artist and not target.artist.artist_songs:
            # If there aren't, delete the artist
            session.delete(target.artist)
