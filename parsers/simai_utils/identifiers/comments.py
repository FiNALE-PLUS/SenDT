from enum import StrEnum


class SentakkiCommentKeys(StrEnum):
    SENTAKKI_IDENTIFIER = 'comment1'
    SONG_TITLE = 'safename'
    SONG_ARTIST = 'artist'
    CHART_AUTHOR = 'author'


class SentakkiCommentValues(StrEnum):
    SENTAKKI_IDENTIFIER_COMMENT = 'Sentakki flavoured simai v0'


