#!/bin/bash -ue
coordinate_system=$(grep coordinate_system standardized_input.tsv-meta.yaml | awk -F ":" '{print $2}' | tr -d "[:blank:]" )
if test -z "$coordinate_system"; then coordinate="1-based"; else coordinate=$coordinate_system; fi
from_build=$((grep genome_assembly standardized_input.tsv-meta.yaml | grep -Eo '[0-9][0-9]') || (echo $(basename standardized_input.tsv) | grep -Eo '[bB][a-zA-Z]*[0-9][0-9]' | grep -Eo '[0-9][0-9]'))
[[ -z "$from_build" ]] && { echo "Parameter from_build is empty" ; exit 1; }

map_to_build_nf.py     -f standardized_input.tsv     -from_build $from_build     -to_build 37     -vcf "/home/dawit/Documents/Projects/rejuve-bio2/GalaxyTools/use-gwaslab/Notebooks/run_workspace/references/homo_sapiens-chr*.parquet"     -chroms "[7]"     -coordinate $coordinate
