import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import OrderedDict, TypedDict

from flatdict import FlatDict

from parsers.simai_utils.comments import FinaleMusicParameters, FinaleTextOutParameters
from utils.finale.validation.music import validate_music_id, validate_finale_music_safename



class SongConfig(TypedDict):
    music_config: FinaleMusicParameters
    textout_config: FinaleTextOutParameters


def validate_music_config(config: SongConfig) -> bool:
    for key, value in FlatDict(config).items():
        if value is None:
            return False

    if not validate_music_id(config["music_config"]["song_id"]):
        return False
    if not validate_finale_music_safename(config["music_config"]["song_safename"]):
        return False

    if (not config["textout_config"]["song_title"]
            or not config["textout_config"]["song_artist"]
            or not config["textout_config"]["chart_author"]):
        return False

    return True


def write_music_config(path: Path, music_config: SongConfig) -> None:
    config_parser = configparser.ConfigParser(dict_type=SongConfig)
    config_parser.read_dict(music_config)

    with open(path, 'w', encoding="utf-8") as configfile:
        config_parser.write(configfile)


def read_music_config(music_config_path: str) -> SongConfig:
    parser = configparser.ConfigParser(dict_type=SongConfig)
    # parser.read(music_config_path)

    with open(music_config_path, 'r', encoding="utf-8") as configfile:
        parser.read_file(configfile)

    song_config = SongConfig(
        music_config=FinaleMusicParameters(
            song_id=parser.getint('music_config', 'song_id', fallback=None),
            song_safename=parser.get('music_config', 'song_safename', fallback=None),
            bpm=parser.get('music_config', 'bpm', fallback=None),
        ),
        textout_config=FinaleTextOutParameters(
            song_title=parser.get('textout_config', 'song_title', fallback=None),
            song_artist=parser.get('textout_config', 'song_artist', fallback=None),
            chart_author=parser.get('textout_config', 'chart_author', fallback=None),
        )
    )

    return song_config
