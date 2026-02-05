#!/bin/bash -ue
basic_qc_nf.py     -f harmonised.tsv     -o harmonised.qc.tsv     --log report.txt     -db /home/dawit/Documents/Projects/rejuve-bio2/GalaxyTools/use-gwaslab/Notebooks/run_workspace/references/rsID.sql
