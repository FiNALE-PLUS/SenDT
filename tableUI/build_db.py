import re
from pathlib import Path

from sqlmodel import Session

from db.fill_db import fill_db_predefined_data
from db.initialise import init_local_db

# TODO: Fill all *vanilla* data from tables


if __name__ == '__main__':

    song_title_pattern = r'(?P<song_title>RST_MUSICTITLE_(?P<song_id>\d{4}))'
    song_artist_pattern = r'(?P<song_artist>RST_MUSICARTIST_(?P<song_artist_id>\d{4}))'
    chart_creator_pattern = r'(?P<chart_creator>RST_SCORECREATOR_(?P<chart_creator_id>\d{4}))'

    column_name_patterns = {
        'safename': re.compile(song_title_pattern),
        'artist': re.compile(song_artist_pattern),
        'chart_creator': re.compile(chart_creator_pattern),
    }

    song_info_key_pattern = re.compile(song_title_pattern +
                                       r'|' + song_artist_pattern +
                                       r'|' + chart_creator_pattern)

    engine = init_local_db(Path("./table_data"))

    # TODO: Add data from songs (for artists, get ID by matching *both* textout artist rows for the song)
    with Session(engine) as session:
        fill_db_predefined_data(session)

        # Table directory here
        raise NotImplementedError('A table directory needs to be set to build a database.')
        tbl_dir = r'TABLE DIR HERE'

        fill_db_from_table_files(
            session,
            Path(tbl_dir) / r'mmMusic.tin',
            Path(tbl_dir) / r'mmScore.tin',
            Path(tbl_dir) / r'mmFesList.tin',
            Path(tbl_dir) / r'mmtextout_ex.tin',
            Path(tbl_dir) / r'mmtextout_jp.tin',
            vanilla_tables=True
        )

        session.commit()



