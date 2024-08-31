"""Functions to work with IFS forecasts in healpix format."""

import numpy as np
import pandas as pd
import cartopy.crs as ccrs

ORCESTRA_DOMAIN = -65, -5, -10, 25  # lon_min, lon_max, lat_min, lat_max
INTERNAL_FIGURE_SIZE = (15, 8)
INTERNAL_PLOTS = ["iwv_itcz_edges", "sfc_winds", "precip", "cloud_top_height",
                  "iwv_itcz_edges_enfo"]

def get_valid_time(
    briefing_time: pd.Timestamp, briefing_lead_hours: str
) -> pd.Timestamp:
    """Valid time for when the briefing info applies."""
    briefing_delta = pd.Timedelta(hours=int(briefing_lead_hours[:-1]))
    valid_time = briefing_time + briefing_delta
    return valid_time


def format_internal_figure_axes(
    briefing_time, lead_hours, issue_time, sattracks_fc_time, plot_type, ax,
    crs=ccrs.PlateCarree(),
):
    lon_min, lon_max, lat_min, lat_max = ORCESTRA_DOMAIN
    valid_time = get_valid_time(briefing_time, lead_hours)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    title_str = (
        f"Valid time: {valid_time.strftime('%Y-%m-%d %H:%M')}UTC"
    )
    ax.set_title(title_str)
    ax.coastlines(lw=1.0, color="k")
    ax.set_xticks(np.round(np.linspace(-70, 10, 9), 0), crs=crs)
    ax.set_yticks(np.round(np.linspace(-20, 20, 5), 0), crs=crs)
    ax.set_ylabel("Latitude / \N{DEGREE SIGN}N")
    ax.set_xlabel("Longitude / \N{DEGREE SIGN}E")
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])
    annotation = _set_annotation(issue_time, sattracks_fc_time, plot_type)
    ax.annotate(
        annotation,
        (-26, -9),
        fontsize=8,
        bbox=dict(facecolor="white", edgecolor="none", alpha=1),
    )


def _set_annotation(
        issue_time: pd.Timestamp,
        sattracks_fc_time: pd.Timestamp,
        plot_type: str,
        ) -> str:
        _validate_plot_type(plot_type)
        if plot_type == "sfc_winds":
            return (f"Red line shows the 48mm contour of integrated column " +
                    f"water vapour.\nLatest ECMWF IFS forecast initialization: " +
                    f"{issue_time.strftime('%Y-%m-%d %H:%M %Z')}\n" +
                    f"Satellite tracks forecast issued on: "
                    f"{sattracks_fc_time.strftime('%Y-%m-%d %H:%M %Z')}")
             
        elif plot_type == "iwv_itcz_edges_enfo":
            return (f"Latest ECMWF IFS forecast initialization: " +
                    f"{issue_time.strftime('%Y-%m-%d %H:%M %Z')}\n" +
                    f"Satellite tracks forecast issued on: "
                    f"{sattracks_fc_time.strftime('%Y-%m-%d %H:%M %Z')}")
             
        else:
            return (f"Red lines show the 48mm contour of integrated column water\n" +
                    f"vapour. The darker the line, the newer the forecast.\n"
                    f"Latest ECMWF IFS forecast initialization: " +
                    f"{issue_time.strftime('%Y-%m-%d %H:%M %Z')}\n" +
                    f"Satellite tracks forecast issued on: "
                    f"{sattracks_fc_time.strftime('%Y-%m-%d %H:%M %Z')}")
        

def _validate_plot_type(plot_type: str) -> None:
    """Check that a correct plot type was provided."""
    msg = f"Incorrect plot_type, should be {INTERNAL_PLOTS}!"
    if plot_type not in INTERNAL_PLOTS:
        raise ValueError(msg)