import re

from colorama import Style, Fore

from parsers.simai_utils.comments import FinaleMusicParameters

from utils.cli.menu.categorical import cli_choice_menu
from utils.finale.validation.music import validate_finale_music_safename


def validate_sentakki_params(params: FinaleMusicParameters) -> bool:
    # Required values
    if (params["song_id"] is None or params["song_safename"] is None
            or params["difficulty_level"] is None or params["difficulty_value"] is None
            or params["song_title"] is None or params["song_title"] is None or params["chart_author"] is None):
        return False

    if not validate_finale_music_safename(params["song_safename"]):
        return False

    # Utage charts must declare their challenge type, and non-utage charts must have no utage challenge type
    if not ((params["difficulty_level"].name.startswith('utage')) ^ (params["utage_type"] is None)):
        return False

    # 1 or no d.p for difficulty values
    if round(params["difficulty_value"], 1) != params["difficulty_value"]:
        return False

    return True


def sentakki_chart_params_main_menu(params: FinaleMusicParameters):
    # TODO: Add menu with readable options and validation for chart completeness (separate function?)

    selectable_items = [item for item in params.items() if item[0] != 'is_sentakki']
    menu_options = [f'{item[0]}: {item[1]}' for item in selectable_items]

    menu_selection = cli_choice_menu(
        selections=menu_options,
        menu_name='Chart Configuration',
        selection_text='Select a chart parameter to configure',
        required_validation=lambda: validate_sentakki_params(params),
    )

    if menu_selection is None:
        return None

    for idx, item in enumerate(selectable_items):
        if menu_selection.startswith(selectable_items[idx][0]):
            return item

    raise ValueError('No valid chart parameter selection found')


def configure_sentakki_chart_params(params: FinaleMusicParameters):
    while (
            menu_selection := sentakki_chart_params_main_menu(params)
    ) is not None:
        # TODO: Add removal of utage challenge type for charts that are made non utage
        match menu_selection:
            case _:
                print(f'Chart parameter {menu_selection} selected.')
