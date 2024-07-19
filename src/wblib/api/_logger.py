"""Log events into the console and save their history."""
import colorama

LOGGED_EVENTS = []

def logger(message: str, level: str) -> None:
    styles = {
        "INFO": colorama.Fore.WHITE,
        "WARNING": colorama.Fore.YELLOW,
        "ERROR": colorama.Fore.RED,
    }
    style = styles[level]
    reset = colorama.Style.RESET_ALL
    print(style + level + ": " + message + reset)
    LOGGED_EVENTS.append({level: message})