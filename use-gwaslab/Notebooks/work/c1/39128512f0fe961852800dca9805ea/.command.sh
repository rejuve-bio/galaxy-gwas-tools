#!/bin/bash -ue
select=$[$(wc -l < 7.merged)]

if [ $[$select/10] -gt 100 ]
then n=$[$select/10]
else n=$select
fi

(head -n 1 7.merged; sed '1d' 7.merged| shuf -n $n)>ten_percent.chr7.merged

header_args=$(utils.py -f 7.merged -strand_count_args);
coordinate_system=$(grep coordinate_system standardized_input.tsv-meta.yaml | awk -F ":" '{print $2}' | tr -d "[:blank:]" )
if test -z "$coordinate_system"; then coordinate="1_base"; else coordinate=$coordinate_system; fi

main_pysam.py     --sumstats ten_percent.chr7.merged     --vcf /home/dawit/Documents/Projects/rejuve-bio2/GalaxyTools/use-gwaslab/Notebooks/run_workspace/references/homo_sapiens-chr7.vcf.gz     $header_args     --strand_counts ten_percent_chr7.sc     --coordinate $coordinate
