import argparse
from pathlib import Path

from colorama import just_fix_windows_console, Style, Fore

from parsers.sentakki import convert_sentakki_file_to_SDB_file
from parsers.simai_utils.chart import get_chart_bpms
from parsers.simai_utils.comments import parse_sentakki_chart_parameters_from_comments, FinaleMusicParameters, \
    FinaleChartParameters
from utils.cli.menu.categorical import cli_choice_menu
from utils.cli.menu.music_config import configure_music_config
from utils.cli.menu.sentakki_params import configure_sentakki_chart_params
from utils.config.music import write_music_config, SongConfig

just_fix_windows_console()

parser = argparse.ArgumentParser(
                    description="Converts Sentakki-Flavoured Simai files to FiNALE's SDT format.",
                    epilog='Text at the bottom of help')
parser.add_argument("-i", "--input", type=str, required=True,
                    help="Path to the Sentakki-Flavoured Simai file to convert.")

parser.add_argument("-o", "--output", type=str, required=True,
                    help="Path for the SDT file to be output to. "
                         "The output file will *always* have the extension `.sdb`. "
                         "If `output` is a directory, the output will stored be within "
                         "the directory with the filename {input_filename}.sdb")

parser.add_argument("-np", "--no-padding", action='store_false', required=False,
                    help="[Not recommended] Removes padding from columns that otherwise align the values within them. "
                         # String formatting requires a second `%` to escape the first
                         r"Greatly reduces readability for debugging purposes "
                         r"in return for a ~1-2%% file size reduction."
                    )
parser.add_argument("--automate_export", action='store_true', required=False,
                    help="Uses leading comments within the simai file to gather information about the chart, "
                         "and uses it to automate exporting to a game directory. "
                         "If required information is missing, the user will be prompted to fill it."
                    )

args = parser.parse_args()

input_path = Path(args.input)
output_path = Path(args.output)

if not input_path.parent.exists():
    raise parser.error(f"The specified input out_path belongs to a directory that does not exist. "
                       f"(Checked {input_path.parent})")


if output_path.is_dir() and not args.automate_export:
    output_path = output_path / (input_path.stem + ".sdb")

else:
    if not output_path.parent.exists():
        raise parser.error(f"The specified output out_path belongs to a directory that does not exist. "
                           f"(Checked {output_path.parent})")

    output_path = output_path.with_suffix(".sdb")
    if output_path.is_file() and output_path.exists():
        response = ""

        while response not in ("y", "n", "yes", "no"):
            response = input(f"This file already exists, do you want to overwrite it? "
                             f"{Fore.LIGHTGREEN_EX}(y/n){Style.RESET_ALL}: ").lower()

        if response in ("n", "no"):
            exit()
        elif response in ("y", "yes"):
            print(f"Proceeding to overwrite `{output_path}`.")

if not args.no_padding:
    print("Padding disabled for this conversion.")


chart_bpm = cli_choice_menu(
    get_chart_bpms(input_path), "BPM selection", "Select a BPM",
    "These BPM values have been found within the simai chart. "
    "Please select the BPM that will be used for `mmMusic`."
)

if args.automate_export:
    # TODO: Get BPMs from all charts in folder, validate input is dir
    print("Automating export.")

    base_chart_file = None

    file_options = []
    if input_path.is_dir():
        for path_entry in input_path.glob('*'):
            if path_entry.suffix in ('simai', 'txt'):
                file_options.append(path_entry)

        if file_options:
            base_chart_file = input_path / cli_choice_menu(
                selections=file_options,
                menu_name='Base Chart Selection',
                selection_text='Select a chart file to base configuration on',
                early_cancel_allowed=True
            )

    else:
        base_chart_file = input_path


    parsed_params = {}

    if base_chart_file is not None:
        with open(base_chart_file, "r") as input_file:
            simai_lines = input_file.readlines()

        # Parse the values from the chart, and then immediately ask the user for any desired changes
        # TODO: Add optional comments for ID and safename? Separate File?
        parsed_params = parse_sentakki_chart_parameters_from_comments(simai_lines)

    final_music_config = configure_music_config(
        starting_config=SongConfig(

        ),
    )

    # write_music_config()

    # TODO: Infer safename from safename when possible
    initial_finale_params = FinaleChartParameters(
            song_id=None, song_safename=None,
            **parsed_params
        )
    # for key in FinaleMusicParameters.keys():
    #     if key not in parsed_params:
    #         parsed_params[key] = None
    chart_params = configure_sentakki_chart_params(
        initial_finale_params
    )

    exit()

print(f"Converting simai chart at: \n "
      f"   {input_path.absolute()}\n"
      f"To SDT chart at:\n"
      f"    {output_path.absolute()}\n")

convert_sentakki_file_to_SDB_file(str(input_path.absolute()), str(output_path.absolute()), args.no_padding, chart_bpm)
