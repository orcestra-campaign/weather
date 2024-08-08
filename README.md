# ORCESTRA Weather Briefings

Weather briefings for PERCUSION.

[http://weather.orcestra-campaign.org/](http://weather.orcestra-campaign.org/)

## Creating a new briefing
Creating a new weather briefing presentations consists of the following steps:

1. Start a new weather briefing, generate its automatic figures, and its quarto files.
2. Add manually the MSS figures to the briefing folder.
3. Check all figures are present in the briefing folder.
4. Add a summary of the weather briefing.
5. Preview the weather briefing presentation.
6. Upload the weather briefing folder to the git repository.

## 1 - Start a new weather briefing, generate its automatic figures, and its quarto files.

Use **wbcli.sh** for this. Initialize a new folder with

```
./wbcli.sh start [BRIEFING_DATE]
```

where [BRIEFING_DATE] has the format "YYYYMMDD". This will create a new folder and copy a quarto template to it. The folder will be located in the inside the briefings folder with a name given by briefing date.

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

## 2 - Add manually the MSS figures to the briefing folder.
Add MSS figures to briefings/[BRIEFING_DATE]/mss folder.

The name of the figures can be seen in briefings/[BRIEFING_DATE]/_metadata.yml

## 3 - Check all figures are present in the briefing folder.

Check the status of the briefing by running

```
./wbcli.sh status [BRIEFING_DATE]
```

this will check that all figures are complete and indicate possible missing ones, including those that need to be added manually to the briefing folder.

## 4 - Add a summary of the weather briefing.
Add a summary of the weather briefing in the quarto file briefings/[BRIEFING_DATE]/main.qmd.


## 5 - Preview the weather briefing presentation

After creating the briefing structure and all necessary figures, you can run
quarto in preview mode, which will open a browser and navigate to the most recently modified file.
Because all source files are built twice (in website and slide mode), the preview mechanism can get confused.
Therefore, when working on a slide, it is best to explicitly run the preview server using the slide profile:
```
quarto preview --profile slides
```

You can also use quarto to build the presentations and website
```
quarto render
```

## 6. Upload the weather briefing foder to the git repository

After checking that the presentation builds correctly, upload the files in the
new briefing folder (briefings/[BRIEFING_DATE]) to the repository.

Create a new branch for this and name it after the briefing date, as "briefing_[BRIEFING_DATE]".

Integrate the new branch to main using a merge request. After integration to the main branch the briefing will be published.


