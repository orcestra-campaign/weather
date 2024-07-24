# ORCESTRA Weather Briefings

Weather briefings for PERCUSION.

## Starting a new briefing

### Generate the briefing figures and initial quarto file with **wbcli.sh**
Initialize a new folder with

```
./wbcli.sh start [BRIEFING_DATE]
```

where [BRIEFING_DATE] has the format "YYYYMMDD". This will create a new briefing folder and copy a quarto template to it.

Create the expected variable file in the folder with

```
./wbcli.sh variables [BRIEFING_DATE] [FLIGHT_NUMBER] [LOCATION]
```

where [LOCATION] must be either Sal or Barbados. This will create a 'yaml' file in the briefing folder and link the '_variables.yml' file to it.

Create the figures of the report with

```
./wbcli.sh figures [BRIEFING_DATE]
```

this will generate the report figures and save them to the corresponding briefing folder.

Check the status of the briefing by running

```
./wbcli.sh status [BRIEFING_DATE]
```

this will check that all figures are complete and indicate possible missing ones, including those that need to be added manually to the briefing folder.

## Generating the weather briefing presentation

### Preview Server

for slide view:

```
./render_quarto.sh [BRIEFING_DATE] preview slides
```

for website view:

```
./render_quarto.sh [BRIEFING_DATE] preview website
```

### Build Everything

```
./render_quarto.sh [BRIEFING_DATE] render slides
./render_quarto.sh [BRIEFING_DATE] render website
```
