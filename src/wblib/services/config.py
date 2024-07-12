"""
Configure the information expected by the weather briefing.
"""

import pathlib

WEATHER_PREDICTION_MODELS = ["IFS", "ICON"]
LEADTIMES = ["000h", "012h", "036h", "060h", "084h", "108h"]
EXTERNAL_PLOTS = [
    "NHC_sfc_analysis",
    "current_satellite_image_vis",
    "current_satellite_image_IR",
    "meteogram_location",
]
INTERNAL_PLOTS = [
    "sfc_pres_wind",
    "IWV_ITCZ_edges",
    "sim_IR_image",
    "cloud_cover",
    "dust_tau550",
]
MSS_PLOTS_SIDE_VIEW = ["relative_humidity", "cloud_cover"]
ALLOWED_LOCATIONS = ["Barbados", "Sal"]

_OUTPATH_TEMPLATE = "briefings/{date}"


def get_briefing_relative_path(date) -> str:
    return _OUTPATH_TEMPLATE.format(date=date)


def get_figures_relative_path(date) -> str:
    return _OUTPATH_TEMPLATE.format(date=date) + "/fig"


def get_expected_external_figures(figures_output_path) -> dict:
    figures = {
        product: f"{figures_output_path}/external/{product}.png"
        for product in EXTERNAL_PLOTS
    }
    return figures


def get_expected_internal_figures(figures_output_path, init) -> dict:
    figures = dict()
    for product in INTERNAL_PLOTS:
        figures[product] = dict()
        for lead_time in LEADTIMES:
            figures[product][f"initplus{lead_time}"] = (
                f"{figures_output_path}/internal/IFS_{init}+{lead_time}_{product}.png"
            )
    return figures


def get_expected_mss_side_view_figures(figures_output_path, init, flight_id) -> dict:
    figures = {
        "IFS": {
            product: f"{figures_output_path}/mss/MSS_{flight_id}_sideview_IFS_{init}_{product}.png"
            for product in MSS_PLOTS_SIDE_VIEW
        },
        "ICON": {
            product: f"{figures_output_path}/mss/MSS_{flight_id}_sideview_ICON_{init}_{product}.png"
            for product in MSS_PLOTS_SIDE_VIEW
        },
    }
    return figures
