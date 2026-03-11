#!/bin/bash -ue
sum_strand_counts_10percent_nf.py     -i /home/dawit/Documents/Projects/rejuve-bio2/GalaxyTools/use-gwaslab/Notebooks/standardized_input/2_ten_sc     -o ten_percent_total_strand_count.tsv     -t 0.99 

s=$(cat ten_percent_total_strand_count.tsv | grep status | awk 'BEGIN {FS="	"}; {print $2}')
mode=$(grep palin_mode ten_percent_total_strand_count.tsv | cut -f2 )

# capture process environment
set +u
set +e
cd "$NXF_TASK_WORKDIR"

nxf_eval_cmd() {
    {
        IFS=$'\n' read -r -d '' "${1}";
        IFS=$'\n' read -r -d '' "${2}";
        (IFS=$'\n' read -r -d '' _ERRNO_; return ${_ERRNO_});
    } < <((printf '\0%s\0%d\0' "$(((({ shift 2; "${@}"; echo "${?}" 1>&3-; } | tr -d '\0' 1>&4-) 4>&2- 2>&1- | tr -d '\0' 1>&4-) 3>&1- | exit "$(cat)") 4>&1-)" "${?}" 1>&2) 2>&1)
}

echo '' > .command.env
#
echo mode="${mode[@]}" >> .command.env
echo /mode/ >> .command.env
#
echo s="${s[@]}" >> .command.env
echo /s/ >> .command.env
