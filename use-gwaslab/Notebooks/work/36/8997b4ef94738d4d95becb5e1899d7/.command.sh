#!/bin/bash -ue
coordinate_system=$(grep coordinate_system standardized_input.tsv-meta.yaml | awk -F ":" '{print $2}' | tr -d "[:blank:]" )
if test -z "$coordinate_system"; then coordinate="1-based"; else coordinate=$coordinate_system; fi

header_args=$(utils.py -f 7.merged -harm_args);

main_pysam.py     --sumstats 7.merged     --vcf /home/dawit/Documents/Projects/rejuve-bio2/GalaxyTools/use-gwaslab/Notebooks/run_workspace/references/homo_sapiens-chr7.vcf.gz     --hm_sumstats chr7.merged_unsorted.hm     --hm_statfile chr7.merged.log.tsv.gz     $header_args     --na_rep_in NA     --na_rep_out NA     --coordinate $coordinate     --palin_mode forward;

chr=$(awk -v RS='	' '/chromosome/{print NR; exit}' chr7.merged_unsorted.hm)
pos=$(awk -v RS='	' '/base_pair_location/{print NR; exit}' chr7.merged_unsorted.hm)

head -n1 chr7.merged_unsorted.hm > chr7.merged.hm;
tail -n+2 chr7.merged_unsorted.hm | sort -n -k$chr -k$pos -T$PWD >> chr7.merged.hm
