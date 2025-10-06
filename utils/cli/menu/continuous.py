from colorama import Fore, Style


def difficulty_value_choice_menu() -> int | float:
    print(f"-------------------- Difficulty Value Selection --------------------")
    selection = None

    while selection is None:
        try:
            choice = float(input(f"Enter chart difficulty {Fore.LIGHTGREEN_EX}[1 - 14]{Style.RESET_ALL}: "))
            if 1 <= choice <= 14:
                # Remove decimal place if possible (i.e 12.0 -> 12)
                if (int_choice := round(choice)) == choice:
                    selection = int_choice
                elif (decimal_choice := round(choice, 1)) == choice:
                    selection = decimal_choice
                else:
                    print(
                        f"{Fore.LIGHTYELLOW_EX}"
                        f"Difficulty value cannot have more than one decimal place."
                        f"{Style.RESET_ALL}"
                    )
            else:
                print(f"{Fore.LIGHTYELLOW_EX}Difficulty value must be between 1 and 14.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.LIGHTYELLOW_EX}Invalid choice.{Style.RESET_ALL}")

    return selection


# TODO
def integer_input_menu() -> int:
    ...