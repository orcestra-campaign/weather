from typing import Optional
import colorama

RAISED_LEVELS = []

def logger(message: str, level: str) -> None:
    styles = {
        "INFO": colorama.Fore.WHITE,
        "WARNING": colorama.Fore.YELLOW,
        "ERROR": colorama.Fore.RED,
    }
    RAISED_LEVELS.append(level)
    style = styles[level]
    reset = colorama.Style.RESET_ALL
    print(style + level + ": " + message + reset)