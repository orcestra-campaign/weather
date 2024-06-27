import os
import pathlib
import sys
import datetime
import yaml

## functions
def validate_date(date_str):
    try:
        datetime.date.fromisoformat(date_str)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def format_date(date_str):
    return date_str[:4] + date_str[5:7] + date_str[8:10]

def find_latest_available_init(date_str):
    expected_latest_init = date_str + 'T0000UTC'
    expected_2nd_latest_init = date_str + 'T1200UTC'

    #if check_init_plot_availability(expected_latest_init):
    #    return expected_latest_init
    #elif check_init_plot_availability(expected_2nd_latest_init):
    #    return expected_2nd_latest_init

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
validate_date(date)
formatted_date = format_date(date)

## user settings
NWP_models = ['IFS', 'ICON']
leadtimes = ['+000', '+012', '+036', '+060', '+084', '+108']
external_plots = [
    'NHC_surface_analysis',
    'current_satellite_image_vis',
    'current_satellite_image_IR'
    ]
internal_plots = [
    'sfc_pres_wind',
    'IWV_ITCZ_edges',
    'sim_IR_image'
    ]
mss_plots_side_view = [
   'relative_humidity',
   'cloud cover'
   ]

# determine latest available initialization
init = find_latest_available_init(formatted_date)

# generate internal plots. FIXME: Add if-clause to only generate plots if not
# already done
# generate_IFS_plots(init)

# set paths where plots are stored
parent_path_plots = '/some/path/somewhere'
plotpath_external = f'{parent_path_plots}/external/{formatted_date}'
plotpath_internal = f'{parent_path_plots}/internal/{init}'
plotpath_mss = {
    NWP_model: f'{parent_path_plots}/mss/{flight}/side_view/{NWP_model}/{init}/'
    for NWP_model in NWP_models
    }

# create dictionary containing variables to be read by quarto template
variables_nml = {
    'date': {
        'yyyy-mm-dd': date,
        'yyyymmdd': formatted_date,
        },
    'plots': {
        'external': {
            product: f'{plotpath_external}/{formatted_date}_{product}.png'
            for product in external_plots
            },
        'internal': {
            product: {
                f'init{lead_time}': f'{plotpath_internal}/IFS_{init}{lead_time}_{product}.png'
                for lead_time in leadtimes
                }
                for product in internal_plots
                },
        'mss_side_view': {
            'IFS': {
                product: f'{plotpath_mss["IFS"]}/{init}/{flight}_side_view_IFS_{init}_{product}.png'
                for product in mss_plots_side_view
                },
            'ICON': {
                product: f'{plotpath_mss["ICON"]}/{init}/{flight}_side_view_ICON_{init}_{product}.png'
                for product in mss_plots_side_view
                },
            },
        }
    }


# generate _variables_nml_{formatted_date}.yml and create link pointing to it
outfile_yml = f'briefings/output/_variables_{formatted_date}.yml'
softlink_yml = '_variables.yml'
print(os.getcwd())
with open(outfile_yml, 'w') as outfile:
    yaml.dump(variables_nml, outfile, default_flow_style=False)
create_softlink(outfile_yml, softlink_yml)