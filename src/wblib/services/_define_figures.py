"""Define the figures and the functions that generate them."""

from wblib.figures.external.noaa import surface_analysis_atlantic


EXTERNAL_PLOTS = {
    "NHC_sfc_analysis": surface_analysis_atlantic,
    "current_satellite_image_vis": None,
    "current_satellite_image_IR": None,
    "meteogram_location": None,
}
INTERNAL_PLOTS = {
    "sfc_pres_wind": None,
    "IWV_ITCZ_edges": None,
    "sim_IR_image": None,
    "cloud_cover": None,
    "dust_tau550": None,
}
INTERNAL_PLOTS_LEADTIMES = ["000h", "012h", "036h", "060h", "084h", "108h"]