"""Define the figures and the functions that generate them."""

from wblib.figures.external.goes import current_satellite_image_ir
from wblib.figures.external.goes import current_satellite_image_vis
from wblib.figures.external.noaa import nhc_hovmoller
from wblib.figures.external.noaa import nhc_seven_days_outlook
from wblib.figures.external.noaa import nhc_surface_analysis_atlantic
from wblib.figures.external.ecmwf import ifs_meteogram
from wblib.figures.external.ecmwf import ifs_dust
from wblib.figures.internal.icwv import iwv_itcz_edges
from wblib.figures.internal.sfc_winds import sfc_winds
from wblib.figures.internal.precip import precip
from wblib.figures.internal.olr import toa_outgoing_longwave


EXTERNAL_INST_PLOTS = {
    "nhc_surface_analysis_atlantic": nhc_surface_analysis_atlantic,
    "nhc_seven_days_outlook": nhc_seven_days_outlook,
    "current_satellite_image_ir": current_satellite_image_ir,
    "nhc_hovmoller": nhc_hovmoller,
    "ifs_meteogram": ifs_meteogram,
}

EXTERNAL_LEAD_PLOTS = {
    "dust": ifs_dust,
}

INTERNAL_PLOTS = {
    "iwv_itcz_edges": iwv_itcz_edges,
    "sfc_winds": sfc_winds,
    "precip": precip,
    "toa_outgoing_longwave": toa_outgoing_longwave
}

INTERNAL_PLOTS_LEADTIMES = ["012h", "036h", "060h", "084h", "108h"]
