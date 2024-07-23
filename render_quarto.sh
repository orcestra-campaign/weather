# render the final quarto file
set -o xtrace

quarto_file=${1}
quarto_command=${2:-preview}
quarto_profile=${3:-slides}

if [ ${quarto_command} = 'preview' ]; then
    quarto preview ${quarto_file} --no-navigate --profile ${quarto_profile}
elif [ ${quarto_command} = 'render' ]; then
    quarto render ${quarto_file} --profile ${quarto_profile}
else
    echo "Please provide a valid quarto command."
    echo "Valid commands are 'preview' and 'render'."
fi
