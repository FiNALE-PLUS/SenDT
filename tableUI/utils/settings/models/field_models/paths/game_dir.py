from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator

from tableUI.utils.settings.models.field_models.paths.existing_dir import optionalExistingAbsoluteDirectory


def existing_finale_game_directory_validation_heuristic(path: Path | None):
    """
    Performs sanity checks to ensure that some of the expected directories and files
    expected within a game image are present, while ignoring those that are most subject to change.
    This heuristic *is not* meant to be a source of 'truth' whether a directory is a game directory or not.

    :param path: The directory to perform sanity checks against.
    :return: The original path, if validated successfully.
    """

    # Defining files that are expected to be present in all installs of the game
    EXPECTED_ROOT_ITEMS = (
        # Dirs
        'data',
        'Firm',
        'LastScreen',
        'Microsoft.VC90.CRT',
        'MiniDump',
        # Files
        'GrooveMaster.ini',
        'SystemConfig.txt'
    )

    DATA_DIRS = (
        'acro', 'filters',
        'font', 'movie',
        'score', 'shader',
        'sound', 'sprite',
        'surfboard', 'surfboard_EN',
        'tables', 'visualizer',
        'whiteboard', 'whiteboard2', 'whiteboard3'
    )

    if path is not None:
        if not isinstance(path, Path):
            raise TypeError(f"Expected Path but got {type(path)}")

        # Get the name of all files/dirs in the root directory
        root_content_names = [i.name for i in path.iterdir()]
        # Only pass if all expected items are present
        if not all(i in root_content_names for i in EXPECTED_ROOT_ITEMS):
            raise ValueError(f'Could not find the following expected items in the root directory:\n\t'
                             # Create an indented list contining all missing items
                             f'\n\t- '
                             f'{'\n\t- '.join(i for i in EXPECTED_ROOT_ITEMS if i not in root_content_names)}\n')

        if not (data_dir := (path / 'data')).exists():
            raise ValueError(f'Could not find a data directory at {data_dir.absolute()}.')

        # Repeat the process for expected directories in `data`
        data_content_names = [i.name for i in (path / 'data').iterdir()]

        if not all(i in data_content_names for i in DATA_DIRS):
            raise ValueError(f'Could not find the following expected items in the data directory:'
                             f'\n\t- '
                             f'{'\n\t- '.join(i for i in DATA_DIRS if i not in data_content_names)}\n')

    return path


optionalFinaleInstallDirectory = Annotated[
    optionalExistingAbsoluteDirectory,
    AfterValidator(existing_finale_game_directory_validation_heuristic)
]
