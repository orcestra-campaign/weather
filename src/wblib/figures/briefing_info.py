"""Functions to work with IFS forecasts in healpix format."""

import numpy as np
import pandas as pd
import cartopy.crs as ccrs

ORCESTRA_DOMAIN = -65, -5, -10, 25  # lon_min, lon_max, lat_min, lat_max

INTERNAL_FIGURE_SIZE = (15, 7)


def get_valid_time(
    briefing_time: pd.Timestamp, briefing_lead_hours: str
) -> pd.Timestamp:
    """Valid time for when the briefing info applies."""
    briefing_delta = pd.Timedelta(hours=int(briefing_lead_hours[:-1]))
    valid_time = briefing_time + briefing_delta
    return valid_time


def format_internal_figure_axes(
    briefing_time, lead_hours, issue_time, ax, crs=ccrs.PlateCarree()
):
    lon_min, lon_max, lat_min, lat_max = ORCESTRA_DOMAIN
    valid_time = get_valid_time(briefing_time, lead_hours)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    title_str = (
        f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')}UTC \n"
        f"Lead hours: {lead_hours}"
    )
    ax.set_title(title_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=crs)
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=crs)
    ax.set_ylabel("Latitude - \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude - \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = f"Latest ECMWF IFS forecast initialization: {issue_time.strftime('%Y-%m-%d %H:%M %Z')}"
    ax.annotate(
        annotation,
        (-28.5, -9),
        fontsize=8,
        bbox=dict(facecolor="white", edgecolor="none", alpha=1),
    )
