import warnings

from wblib.api.api import weather_briefing_api

warnings.filterwarnings(
    action="ignore",
    message="",
    category=FutureWarning,
    module="intake_xarray",
)
