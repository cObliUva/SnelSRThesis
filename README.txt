Modelling decision-making strategies better than participants' self-report, predictions on the continuation of binary outcomes.

Author: Caspar Fermin - 12854980
Cognition, Language & Communication, University of Amsterdam
Thesis - Program Synthesis
Supervisor: Fausto Carcassi
June 24, 2025

The data was downloaded from the osf: https://osf.io/2d93t/files/osfstorage
The data was produced by the study of Rao & Hastie (2023) - https://doi.org/10.1111/cogs.13211

The purpose of the research was to find interpretable symbolically regressed rules which represented participants decision-making strategy.

The current paths in the analysis files that read the datafiles might not be functional. Do not run LoT.py, as it requires too much processing power and may run for hours. If reproduction is desired use the LoT1B/2B.csv files to find the best rules, the names of the csv that reads and writes need to be changed if you want to analyse both experiments. The best rules can then be generalized using the BayInf.py file, again the paths need to be adjusted and the file needs to be ran twice. This is also the case not the case for InterpretRule.py or ModVerPlot.Rmd.

Lastly, the job script run_job.sh is included if full reproduction is wanted. Note that all figures in the Thesis can be recreated by running the ModVerPlot file.
