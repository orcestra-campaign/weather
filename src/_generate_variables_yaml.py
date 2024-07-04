import os
import pathlib
import sys
import yaml
from datetime import datetime

## functions
def validate_location(loc):
    try:
        if loc not in ['Barbados', 'Sal']:
            raise ValueError
    except ValueError:
        print("Incorrect location, should be 'Sal' or 'Barbados'!")

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYYMMDD")


def format_date(date_str):
    return date_str[:4] + '-' + date_str[4:6] + '-' + date_str[6:8]

def find_latest_available_init(date_str):
    expected_latest_init = date_str + 'T0000Z'
    expected_2nd_latest_init = date_str + 'T1200Z'

    #if check_init_plot_availability(expected_latest_init):
    #    return expected_latest_init
    #elif check_init_plot_availability(expected_2nd_latest_init):
    #    return expected_2nd_latest_init
    return expected_latest_init

def create_softlink(file, link):
    # Convert to pathlib.Path objects for easier manipulation
    file_a_path = pathlib.Path(file)
    link_path = pathlib.Path(link)
    
    # Check if the link already exists
    if link_path.exists() or link_path.is_symlink():
        # Remove the existing link
        link_path.unlink()
    
    # Create a new soft link
    link_path.symlink_to(file_a_path)

# ------------------------------------------------------------------------------
## preparations
date = sys.argv[1]
flight = sys.argv[2]
location = sys.argv[3]
validate_date(date)
validate_location(location)
formatted_date = format_date(date)

## user settings
NWP_models = ['IFS', 'ICON']
leadtimes = ['000h', '012h', '036h', '060h', '084h', '108h']
external_plots = [
    'NHC_sfc_analysis',
    'current_satellite_image_vis',
    'current_satellite_image_IR',
    'meteogram_location'
    ]
internal_plots = [
    'sfc_pres_wind',
    'IWV_ITCZ_edges',
    'sim_IR_image',
    'cloud_cover',
    'dust_tau550'
    ]
mss_plots_side_view = [
   'relative_humidity',
   'cloud_cover'
   ]

# determine latest available initialization
init = find_latest_available_init(date)

# generate internal plots. FIXME: Add if-clause to only generate plots if not
# already done
# generate_IFS_plots(init)

# set paths where plots are stored
#parent_path_plots = '/Users/henningfranke/PERCUSION/plots'
parent_path_plots = 'plots'
plotpath_external = f'{parent_path_plots}/external/{date}'
plotpath_internal = f'{parent_path_plots}/internal/IFS/{init}'
plotpath_mss = {
    NWP_model: f'{parent_path_plots}/mss/{flight}/{NWP_model}/{init}/'
    for NWP_model in NWP_models
    }

# create dictionary containing variables to be read by quarto template
variables_nml = {
    'flight': flight,
    'location': location,
    'date': {
        'yyyy-mm-dd': formatted_date,
        'yyyymmdd': date,
        },
    'plots': {
        'external': {
            product: f'{plotpath_external}/{product}.png'
            for product in external_plots
            },
        'internal': {
            product: {
                f'initplus{lead_time}': f'{plotpath_internal}/IFS_{init}+{lead_time}_{product}.png'
                for lead_time in leadtimes
                }
                for product in internal_plots
                },
        'mss_side_view': {
            'IFS': {
                product: f'{plotpath_mss["IFS"]}/{flight}_sideview_IFS_{init}_{product}.png'
                for product in mss_plots_side_view
                },
            'ICON': {
                product: f'{plotpath_mss["ICON"]}/{flight}_sideview_ICON_{init}_{product}.png'
                for product in mss_plots_side_view
                },
            },
        }
    }


# generate _variables_nml_{date}.yml and create link pointing to it
outfile_yml = f'briefings/_variables_{date}.yml'
softlink_yml = '_variables.yml'
print(os.getcwd())
with open(outfile_yml, 'w') as outfile:
    yaml.dump(variables_nml, outfile, default_flow_style=False)
create_softlink(outfile_yml, softlink_yml)
