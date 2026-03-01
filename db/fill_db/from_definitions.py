from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from db.models import SongGenre, UtageType, ChartDifficultyLevel
from utils.finale.difficulties import FinaleUtageType, FinaleChartDifficulty


class DBConfigurationError(ValueError):
    """
    Denotes an error with the way that the database is currently configured.
    Generally, this is raised when a DB contains data that does not match defined expectations,
    such as tables being used as enums not containing the expected values at a defined ID.
    """
    pass

# TODO: Look into dynamically generating errors based on enum fields

# class IncorrectlyDefinedDBEnum(DBConfigurationError):
#     def __init__(self, enum_expected, enum_value):
#         self.enum_expected = enum_expected


def fill_db_predefined_data(session: Session):
    fill_db_genres(session)
    fill_db_utage_types(session)

    fill_db_difficulty_levels(session)

    session.commit()


def fill_db_difficulty_levels(session: Session):
    for difficulty_level in FinaleChartDifficulty:
        chart_difficulty_model = ChartDifficultyLevel(
            id=difficulty_level.value,
            name=difficulty_level.name,
        )

        try:
            existing_difficulty_level = session.exec(
                select(ChartDifficultyLevel).where(ChartDifficultyLevel.id == difficulty_level.value)
            ).one()

            if not existing_difficulty_level.name == difficulty_level.name:
                raise DBConfigurationError(
                    f"Difficulty Level {difficulty_level.value} contains values that do not match the vanilla game.\n"
                    f"Expected:\n\tName: {difficulty_level.name}\n"
                    f"Got:\n\tName: {existing_difficulty_level.name}"
                )
        except NoResultFound:
            session.add(chart_difficulty_model)

    session.commit()

def fill_db_utage_types(session: Session):
    for utage_type in FinaleUtageType:
        utage_model = UtageType(
            id=utage_type.id,
            name=utage_type.name,
            kanji=utage_type.kanji,
        )

        try:
            existing_utage_type = session.exec(
                select(UtageType).where(UtageType.id == utage_type.id)
            ).one()


            if not existing_utage_type.name == utage_type.name and existing_utage_type.kanji == utage_type.kanji:
                raise DBConfigurationError(
                    f"Utage Type {utage_type.id} contains values that do not match the vanilla game.\n"
                    f"Expected:\n\tName: {utage_type.name}\n\tKanji: {utage_type.kanji}\n"
                    f"Got:\n\tName: {existing_utage_type.name}\n\tKanji: {existing_utage_type.kanji}\n"
                )
        except NoResultFound:
            session.add(utage_model)

    session.commit()

def fill_db_genres(session: Session):
    genres = (
        SongGenre(
            id=4,
            name_en=r'POPS ＆ ANIME',
            name_jp=r'POPS ＆ アニメ'
        ),
        SongGenre(
            id=5,
            name_en=r'niconico ＆ VOCALOID™',
            name_jp=r'niconico ＆ ボーカロイド™'
        ),
        SongGenre(
            id=6,
            name_en=r'TOHO Project',
            name_jp=r'東方Project'
        ),
        SongGenre(
            id=7,
            name_en=r'SEGA',
            name_jp=r'SEGA'
        ),
        SongGenre(
            id=8,
            name_en=r'GAME ＆ VARIETY',
            name_jp=r'ゲーム ＆ バラエティ'
        ),
        SongGenre(
            id=9,
            name_en=r'ORIGINAL ＆ JOYPOLIS',
            name_jp=r'オリジナル ＆ ジョイポリス'
        ),
    )

    for genre in genres:
        try:
            existing_genre = session.exec(
                select(SongGenre).where(SongGenre.id == genre.id)
            ).one()

            if existing_genre.name_en == genre.name_en and existing_genre.name_jp == genre.name_jp:
                continue
            else:
                raise DBConfigurationError(
                    f"Genre {genre.id} contains genre names that do not match the vanilla game.\n"
                    f"Expected:\n\tEX: {genre.name_en}\n\tJP: {genre.name_jp}\n"
                    f"Got:\n\tEX: {existing_genre.name_en}\n\tJP: {existing_genre.name_jp}\n"
                )

        except NoResultFound:
            session.add(genre)

    session.commit()
