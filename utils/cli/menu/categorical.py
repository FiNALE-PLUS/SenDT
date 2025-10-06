from enum import Enum
from typing import Callable

from colorama import Fore, Style

from utils.finale.difficulties import FinaleChartDifficulty, FinaleUtageType

EXIT_MENU_STR = 'x'

def cli_choice_menu(selections: list, menu_name: str, selection_text: str, menu_desc: str | None = None,
                    selection_ids: list[int] | None = None,
                    early_cancel_allowed: bool = False, required_validation: Callable[[], bool] | None = None, ):
    """
    Displays a menu within the console for the user, returning the value selected when a valid ID is selected.
    The function will not return until a valid selection is made.

    :param selections: The values to be returned when the relevant selection is made.

    :param menu_name: The name of the menu to be displayed above all menu options.

    :param selection_text: The base string to print for the user's prompt to make a choice

    :param menu_desc: A string to be printed below the safename of the menu, before the options.

    :param selection_ids: The IDs that can be entered to select a value.
        If not provided, each value will be provided a consecutive number, starting with 1.

    :param early_cancel_allowed: Denotes whether the menu can be cancelled without entering an option.
        When used, entering `x` will exit the menu and return `None`.

    :param required_validation: A function with no arguments that returns True when the input data is valid,
        and False otherwise. The function must be able to be called an arbitrary number of times.
        When used, the menu name will be appended with the validity of the current data.
        Additionally, when ``early_cancel_allowed`` is set to `False`, the menu will only allow for cancellation
        when ``required_validation`` evaluates to `True`.

    :return: The selected value, or `None` if cancelled.
    """

    if selection_ids is not None:
        if len(selection_ids) != len(selections):
            raise ValueError(f'Number of selection values does not match number of choices '
                             f'({len(selections)} choices, {len(selection_ids)} values)')
        if len(set(selection_ids)) != len(selections):
            raise ValueError(f'Selection IDs must be unique.')
    else:
        selection_ids = [i + 1 for i in range(len(selections))]

    if early_cancel_allowed and EXIT_MENU_STR in selection_ids:
        raise ValueError(f'CANCEL_MENU_STR ({EXIT_MENU_STR}) must not be in '
                         f'{selection_ids} when the menu can be exited.')

    # Display validation state when applicable
    title = menu_name
    if required_validation is not None:
        title += f' [currently {Style.BRIGHT}{Fore.LIGHTGREEN_EX + "valid" if required_validation()
                  else Fore.LIGHTRED_EX + "invalid"}{Style.RESET_ALL}]'
    print(f"-------------------- {title} --------------------")

    if menu_desc is not None:
        print(menu_desc)

    for idx, choice in enumerate(selections):
        print(f"{Fore.LIGHTGREEN_EX}[{selection_ids[idx]}]{Style.RESET_ALL}: "
              f"{Style.BRIGHT}{choice}{Style.RESET_ALL}")
    print()

    choice = -1

    while choice not in selection_ids:
        menu_cancellable = (required_validation is None or required_validation()) or early_cancel_allowed
        try:
            # {Fore.LIGHTGREEN_EX}[1 - {selection_ids[-1]}]
            choice = input(f"{selection_text}"
                           f"{f' [{EXIT_MENU_STR} to exit]' if menu_cancellable else ''}: ")

            if choice.lower() == EXIT_MENU_STR and menu_cancellable:
                return None
            else:
                choice = int(choice)

        except ValueError:
            print(f"{Fore.LIGHTYELLOW_EX}Invalid selection value.{Style.RESET_ALL}")
        else:
            if choice not in selection_ids:
                print(f"{Fore.LIGHTYELLOW_EX}Your choice must be an integer from the options provided.{Style.RESET_ALL}")

    return selections[selection_ids.index(choice)]


def difficulty_enum_choice_menu():
    menu_choices = [choice for choice in FinaleChartDifficulty]
    selection_values = [choice.value for choice in FinaleChartDifficulty]

    selection = cli_choice_menu(
        selections=menu_choices, menu_name='Chart Difficulty Selection',
        selection_text='Please select the chart difficulty level', selection_ids=selection_values
    )

    return selection


def utage_type_enum_choice_menu():
    menu_choices = [choice for choice in FinaleUtageType]
    selection_values = [choice.id for choice in FinaleUtageType]

    selection = cli_choice_menu(
        selections=menu_choices, menu_name='Utage Chart Type Selection',
        selection_text='Please select the chart utage type', selection_ids=selection_values
    )

    return selection
