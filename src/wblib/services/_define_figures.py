"""Define the figures and the functions that generate them."""

from wblib.figures.external.goes import current_satellite_image_ir
from wblib.figures.external.goes import current_satellite_image_vis
from wblib.figures.external.noaa import nhc_surface_analysis_atlantic


EXTERNAL_PLOTS = {
    "nhc_surface_analysis_atlantic": nhc_surface_analysis_atlantic,
    "current_satellite_image_vis": current_satellite_image_vis,
    "current_satellite_image_ir": current_satellite_image_ir,
}

INTERNAL_PLOTS = {
    "sfc_pres_wind": None,
    "iwv_itcz_edges": None,
    "sim_IR_image": None,
    "cloud_cover": None,
    "dust_tau550": None,
}
INTERNAL_PLOTS_LEADTIMES = ["000h", "012h", "036h", "060h", "084h", "108h"]