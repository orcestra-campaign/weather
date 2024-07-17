"""Command Line Interface of the Weather Briefing."""

import argparse

from wblib.api.status import check_briefing_status
from wblib.api.directory import make_briefing_directory
from wblib.api.variables_file import make_briefing_variables
from wblib.api.images import make_briefing_images


ARGUMENT_DESCRIPTIONS = {
    "date": "Issue date of the weather briefing",
    "flight_id": "ID of the flight",
    "location": "Either 'Barbados' or 'Sal'",
}


def weather_briefing_api() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and check PERCUSION Weather Briefings."
    )
    subparsers = parser.add_subparsers(
        title="Available commands", dest="command"
    )
    _define_status_subcommand(subparsers)
    _define_start_subcommand(subparsers)
    _define_variable_subcommand(subparsers)
    _define_figures_subcommand(subparsers)
    _run_chosen_subcommand(parser)


def _run_chosen_subcommand(parser):
    args = parser.parse_args()
    if args.command:
        if args.command in ["status", "start", "figures"]:
            args.func(args.date)
        else:
            args.func(args.date, args.flight_id, args.location)
    else:
        parser.print_help()


def _define_figures_subcommand(subparsers):
    figures_parser = subparsers.add_parser(
        "figures", help="Generate the figures of the weather report."
    )
    figures_parser.add_argument("date", help=ARGUMENT_DESCRIPTIONS["date"])
    figures_parser.set_defaults(func=make_briefing_images)


def _define_variable_subcommand(subparsers):
    variable_file_parser = subparsers.add_parser(
        "variables",
        help="Generate the variable yaml file used by the quarto template.",
    )
    variable_file_parser.add_argument(
        "date", help=ARGUMENT_DESCRIPTIONS["date"]
    )
    variable_file_parser.add_argument(
        "flight_id", help=ARGUMENT_DESCRIPTIONS["flight_id"]
    )
    variable_file_parser.add_argument(
        "location", help=ARGUMENT_DESCRIPTIONS["location"]
    )
    variable_file_parser.set_defaults(func=make_briefing_variables)


def _define_start_subcommand(subparsers):
    mkdir_parser = subparsers.add_parser(
        "start", help="Start a briefing for a new date."
    )
    mkdir_parser.add_argument("date", help=ARGUMENT_DESCRIPTIONS["date"])
    mkdir_parser.set_defaults(func=make_briefing_directory)


def _define_status_subcommand(subparsers):
    status_parser = subparsers.add_parser(
        "status", help="Check the status of the weather briefing."
    )
    status_parser.add_argument("date", help=ARGUMENT_DESCRIPTIONS["date"])
    status_parser.set_defaults(func=check_briefing_status)


if __name__ == "__main__":
    weather_briefing_api()
