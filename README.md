# HPLC-plotter
app to automatically plot Jasco HPLC analyses from an experiment and store the data as csv

To use it, modify the configuration files with your own parameters and then run the executable file for mac or the python script.

How to use the configuration file:

1) Indicate the location of the folder where you want to save your result files, and the name that you want to give to the result files.
2) List the directories of the csv files that you want to plot, separate the diferent directories with a comma and a space ", ".
3) Define the time range of your chromatogram where the normalization should take place. Within this range, your peak of interest should be the most intense signal, and the lowest signal (baseline) will be set to 0.
4) Define the time range of the chromatogram that you want to represent in the plot. This may or may not match with your normalization range.
5) Define the interval between major ticks (the default 5 means 1 tick every 5 minutes) and the number of minor ticks in between (the default 4 means 1 minor tick every minute).

The style section can be modified to change the appearance of the plot. The default values are recommended for good looking traces.
