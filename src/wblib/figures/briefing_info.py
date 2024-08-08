"""Functions to work with IFS forecasts in healpix format."""
import pandas as pd

def get_valid_time(
    briefing_time: pd.Timestamp, briefing_lead_hours: str
) -> pd.Timestamp:
    """Valid time for when the briefing info applies."""
    briefing_delta = pd.Timedelta(hours=int(briefing_lead_hours[:-1]))
    valid_time = briefing_time + briefing_delta
    return valid_time