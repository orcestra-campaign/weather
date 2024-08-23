import xarray as xr
import pandas as pd
from orcestra.meteor import get_meteor_track
from wblib.figures.hifs import get_valid_time

METEOR_PLOT = {
    "COLOR": "mediumorchid",
    "EDGE_COLOR": "black",
    "MARKER": "h",
    "SIZE": 180,
    "ZORDER": 10,
    }

def plot_meteor_latest_position_in_ifs_forecast(
        briefing_time: pd.Timestamp, lead_hours: str, ax,
        meteor: xr.Dataset=None, **kwargs):
    valid_time = get_valid_time(briefing_time, lead_hours)
    if briefing_time.date() == valid_time.date():
        plot_meteor_latest_position(ax, meteor, **kwargs)


def plot_meteor_latest_position(
        ax, meteor: xr.Dataset=None, **kwargs
        ):
    if not meteor: meteor = get_meteor_track(deduplicate_latlon=True)
    meteor_pos = meteor.isel(time=-1)
    _plot_meteor_scatter(meteor_pos, ax)


def plot_meteor_position(
        time: pd.Timestamp, ax, meteor: xr.Dataset=None
        ):
    if not meteor: meteor = get_meteor_track(deduplicate_latlon=True)
    meteor_pos = meteor.sel(time=time, method="nearest")
    _plot_meteor_scatter(meteor_pos, ax)


def plot_meteor_track(
        ax, meteor: xr.Dataset=None, **kwargs
        ):
    if not meteor: meteor = get_meteor_track(deduplicate_latlon=True)
    ax.plot(meteor["lon"], meteor["lat"], **kwargs)


def _plot_meteor_scatter(meteor_pos: xr.Dataset, ax):
    ax.scatter(meteor_pos["lon"], meteor_pos["lat"],
               color=METEOR_PLOT["COLOR"],
               edgecolors=METEOR_PLOT["EDGE_COLOR"],
               marker=METEOR_PLOT["MARKER"],
               s=METEOR_PLOT["SIZE"],
               zorder=METEOR_PLOT["ZORDER"])