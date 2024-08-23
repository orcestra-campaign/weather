import pandas as pd
from orcestra.meteor import get_meteor_track
from wblib.figures.hifs import get_valid_time


def plot_meteor_latest_position_in_ifs_forecast(
        briefing_time: pd.Timestamp, lead_hours: str, ax, **kwargs):
    valid_time = get_valid_time(briefing_time, lead_hours)
    if briefing_time.date() == valid_time.date():
        plot_meteor_latest_position(ax, **kwargs)


def plot_meteor_latest_position(ax, **kwargs):
    meteor = get_meteor_track(deduplicate_latlon=True)
    meteor_latest = meteor.isel(time=-1)
    ax.scatter(meteor_latest["lon"], meteor_latest["lat"], **kwargs)


def plot_meteor_position(time: pd.Timestamp, ax, **kwargs):
    meteor = get_meteor_track(deduplicate_latlon=True)
    meteor_pos = meteor.sel(time=time, method="nearest")
    ax.scatter(meteor_pos["lon"], meteor_pos["lat"], **kwargs)


def plot_meteor_track(ax, **kwargs):
    meteor = get_meteor_track(deduplicate_latlon=True)
    ax.plot(meteor["lon"], meteor["lat"], **kwargs)