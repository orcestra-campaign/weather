"""Check if the information on a briefing is complete."""

from enum import Enum, auto
from pathlib import Path
from typing import Callable

import colorama
import yaml

from wblib.services.get_paths import get_briefing_path
from wblib.services.get_paths import get_briefing_paths
from wblib.services.get_paths import get_variables_path


class Status(Enum):
    INCOMPLETE = auto()
    READY_FOR_QUARTO = auto()


def check_briefing_status(date: str) -> None:
    status = Status.READY_FOR_QUARTO
    reason = ""
    status, reason = _check_briefing_folder_exists(date, status, reason)
    status, reason = _check_briefing_subfolders_exists(date, status, reason)
    status, reason = _check_variables_files_exists(date, status, reason)
    status, reason = _check_external_inst_images_exists(date, status, reason)
    status, reason = _check_external_lead_images_exists(date, status, reason)
    status, reason = _check_internal_images_exists(date, status, reason)
    reset = colorama.Style.RESET_ALL
    if status == Status.READY_FOR_QUARTO:
        style = colorama.Fore.GREEN
        print(
            style + "Briefing data ready. Please continue with Quarto." + reset
        )
        return
    else:
        style = colorama.Fore.RED
        print(style + f"ERROR. Incomplete briefing data for '{date}'" + reset)
        print(style + reason + reset)
        return


def _check_briefing_folder_exists(date, status, reason) -> tuple[Status, str]:
    if status == Status.INCOMPLETE:
        return status, reason
    briefing_path = Path(get_briefing_path(date))
    if not briefing_path.exists():
        status = Status.INCOMPLETE
        reason = f"No briefing folder for '{date}'"
    return status, reason


def _check_briefing_subfolders_exists(
    date, status, reason
) -> tuple[Status, str]:
    if status == Status.INCOMPLETE:
        return status, reason
    briefing_paths = [Path(path) for path in get_briefing_paths(date)]
    for briefing_path in briefing_paths:
        if not briefing_path.exists():
            status = Status.INCOMPLETE
            reason = f"Briefing path '{briefing_path}' not found"
    return status, reason


def _check_variables_files_exists(date, status, reason) -> tuple[Status, str]:
    if status == Status.INCOMPLETE:
        return status, reason
    variables_path = Path(get_variables_path(date))
    if not variables_path.exists():
        status = Status.INCOMPLETE
        reason = f"No variables file for '{date}'"
    return status, reason


def _check_external_inst_images_exists(
        date, status, reason
        ) -> tuple[Status, str]:
    if status == Status.INCOMPLETE:
        return status, reason
    variables_path = Path(get_variables_path(date))
    with open(variables_path, "r") as file:
        variables = yaml.safe_load(file)
    for plot_name, plot_path_str in variables["plots"]["external_inst"].items():
        plot_path = Path(plot_path_str)
        if not plot_path.exists():
            status = Status.INCOMPLETE
            reason = f"External instantaneous plot '{plot_name}' not found."
            break
    return status, reason


def _check_external_lead_images_exists(
        date, status, reason
        ) -> tuple[Status, str]:
    if status == Status.INCOMPLETE:
        return status, reason
    variables_path = Path(get_variables_path(date))
    with open(variables_path, "r") as file:
        variables = yaml.safe_load(file)
    for plot_name, plot_path_str in variables["plots"]["external_lead"].items():
        plot_path = Path(plot_path_str)
        if not plot_path.exists():
            status = Status.INCOMPLETE
            reason = f"External lead time plot '{plot_name}' not found."
            break
    return status, reason


def _check_internal_images_exists(date, status, reason) -> tuple[Status, str]:
    if status == Status.INCOMPLETE:
        return status, reason
    variables_path = Path(get_variables_path(date))
    with open(variables_path, "r") as file:
        variables = yaml.safe_load(file)
    for plot_root, horizon_dict in variables["plots"]["internal"].items():
        for horizon, plot_path_str in horizon_dict.items():
            plot_path = Path(plot_path_str)
            if not plot_path.exists():
                status = Status.INCOMPLETE
                reason = f"Internal plot '{plot_root}' not found for horizon {horizon}."
                break
    return status, reason


if __name__ == "__main__":
    check_briefing_status("20240821")  # for testing
