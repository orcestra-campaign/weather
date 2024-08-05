"""Define the figures and the functions that generate them."""

from wblib.figures.external.goes import current_satellite_image_ir
from wblib.figures.external.goes import current_satellite_image_vis
from wblib.figures.external.noaa import nhc_hovmoller
from wblib.figures.external.noaa import nhc_seven_days_outlook
from wblib.figures.external.noaa import nhc_surface_analysis_atlantic
from wblib.figures.external.ecmwf import ifs_meteogram
from wblib.figures.internal.icwv import iwv_itcz_edges


EXTERNAL_PLOTS = {
    "nhc_surface_analysis_atlantic": nhc_surface_analysis_atlantic,
    "nhc_seven_days_outlook": nhc_seven_days_outlook,
    "current_satellite_image_vis": current_satellite_image_vis,
    "current_satellite_image_ir": current_satellite_image_ir,
    "nhc_hovmoller": nhc_hovmoller,
    "ifs_meteogram": ifs_meteogram,
}

INTERNAL_PLOTS = {
    "iwv_itcz_edges": iwv_itcz_edges
}
INTERNAL_PLOTS_LEADTIMES = ["003h", "012h", "036h", "060h", "084h", "108h"]