# county-vote-disaggregation


This repo contains the data and analysis used for the MGGG `Disaggregation of Unsorted Votes' report found at [INSERT PERMALINK]

The data directory contains shapefiles, voter history files, and election returns for North Carolina and Oklahoma.

Users can run the disaggregation_run_script.py to generate disaggregation estimates.  A state ['NC' or 'OK'] should be specified.

Once that data is generated, the figure_script.py can be run to generate figures used in the report. Alternatively the figure_script can be run without having to first run the disaggregation script by setting data_dir = './output_data_report/' 

The output_data_report directory contains the output data from disaggregation_run_script that was used in the report.  Users can use this data to generate figures (and do other summary analysis) without having to first run disaggregation_run_script.py.