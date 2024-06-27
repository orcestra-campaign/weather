#conda activate weather_briefing_env

# user-defined input variables
briefing_date=${1}
flight=${2}

# 
python3 briefings/_generate_variables_yaml.py ${briefing_date} ${flight}
#quarto preview ./briefings/briefing_template.qmd --no-navigate --profile slides
quarto render --profile slides
