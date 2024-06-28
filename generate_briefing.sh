# activate conda environment
#conda activate weather_briefing_env

# USER ARGUMENTS
# (1) Date when briefing will take place. Has to be provided as yyyymmdd.
briefing_date=${1}

# (2) Name of the flight which should be discussed in briefing.
flight=${2}

# (3) Location where briefing will take place. Either 'Sal' or 'Barbados'.
location=${3}

# (4) Action which should be executed in quarto. Either 'preview' or 'render'.
quarto_command=${4:-preview}

# (5) Target format of quarto action. Either 'slides' or 'website'.
quarto_profile=${5:-slides}

# ------------------------------------------------------------------------------
# create _variables.yml, which contains the paths to all plots
python3 src/_generate_variables_yaml.py ${briefing_date} ${flight} ${location}

# render the final quarto file
quarto_file=./briefings/briefing_${briefing_date}.qmd
if [ ${quarto_command} = 'preview' ]; then
    quarto preview ${quarto_file} --no-navigate --profile ${quarto_profile}
elif [ ${quarto_command} = 'render' ]; then
    quarto render ${quarto_file} --profile ${quarto_profile}
else
    echo "Please provide a valid quarto command."
    echo "Valid commands are 'preview' and 'render'."
fi