from flatdict import FlatDict

from parsers.simai_utils.comments import FinaleMusicParameters, FinaleTextOutParameters
from utils.cli.menu.categorical import cli_choice_menu
from utils.cli.menu.continuous import integer_input_menu
from utils.config.music import SongConfig, validate_music_config


def configure_music_config(starting_config: SongConfig | None = None):
    music_config = SongConfig(
        music_config=FinaleMusicParameters(
            song_id=None,
            song_safename=None,
            bpm=None,
        ),
        textout_config=FinaleTextOutParameters(
            song_title=None,
            song_artist=None,
            chart_author=None,
        )
    )
    if starting_config is not None:
        for upper_key in starting_config:
            for lower_key in starting_config[upper_key]:
                music_config[upper_key][lower_key] = starting_config[upper_key][lower_key]

    while (category_selection := cli_choice_menu(
        selections=[f'{key}: {value}' for key, value in FlatDict(music_config).items()],
        menu_name=f'Music Table Configuration (currently )',
        selection_text='Select a parameter to configure',
        early_cancel_allowed=validate_music_config(music_config),
        required_validation=lambda: validate_music_config(music_config),
    )) is not None:
        if category_selection.startswith('song_id'):
            # TODO
            music_config["music_config"]["song_id"] = integer_input_menu()

    return music_config
