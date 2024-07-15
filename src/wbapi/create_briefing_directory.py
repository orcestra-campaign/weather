"""Create the briefing folder and subfolder."""
import pathlib
import sys

from wblib.services import get_briefing_path
from wblib.services import get_briefing_paths



def make_briefing_folder(date = None) -> None:
    if not date:
        date = sys.argv[1]
    briefing_parent_path = pathlib.Path(get_briefing_path(date))
    briefing_paths = get_briefing_paths(date)
    briefing_parent_path.mkdir(parents=True, exist_ok=True)
    for briefing_path_str in briefing_paths:
        briefing_path = pathlib.Path(briefing_path_str)
        briefing_path.mkdir(parents=False, exist_ok=True)

if __name__ == "__main__":
    #make_briefing_folder(date = "20240101") # for testing
    make_briefing_folder(date = "20240101")

