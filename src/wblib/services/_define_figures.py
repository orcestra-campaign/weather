"""Define the figures and the functions that generate them."""

from wblib.figures.external.goes import current_satellite_image_ir
from wblib.figures.external.goes_2_go import latest_goes2go_image
from wblib.figures.external.goes_2_go import yesterdays_goes2go_image
from wblib.figures.external.noaa import nhc_hovmoller
from wblib.figures.external.noaa import nhc_seven_days_outlook
from wblib.figures.external.noaa import nhc_surface_analysis_atlantic
from wblib.figures.external.ecmwf import ifs_meteogram
from wblib.figures.external.ecmwf import ifs_dust
from wblib.figures.external.ecmwf import ifs_total_aerosol
from wblib.figures.internal.icwv import iwv_itcz_edges
from wblib.figures.internal.sfc_winds import sfc_winds
from wblib.figures.internal.precip import precip
from wblib.figures.internal.cld_top_height import cloud_top_height
from wblib.figures.internal.icwv_ens import iwv_itcz_edges_enfo

EXTERNAL_INST_PLOTS = {
    "nhc_surface_analysis_atlantic": nhc_surface_analysis_atlantic,
    "nhc_seven_days_outlook": nhc_seven_days_outlook,
    "current_satellite_image_ir": current_satellite_image_ir,
    "latest_goes2go_image": latest_goes2go_image,
    "yesterdays_goes2go_image": yesterdays_goes2go_image,
    "nhc_hovmoller": nhc_hovmoller,
    "ifs_meteogram": ifs_meteogram,
}

EXTERNAL_LEAD_PLOTS = {
    "total_aerosol": ifs_total_aerosol,
}

INTERNAL_PLOTS = {
    "iwv_itcz_edges": iwv_itcz_edges,
    "sfc_winds": sfc_winds,
    "precip": precip,
    "cloud_top_height": cloud_top_height,
    "iwv_itcz_edges_enfo": iwv_itcz_edges_enfo,
}

PLOTS_LEADTIMES = ["015h", "039h", "063h", "087h", "108h"]
