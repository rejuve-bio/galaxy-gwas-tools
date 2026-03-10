#!/bin/bash -ue
head -q -n1 *.merged.hm | head -n1 > harmonised.tsv
for c in $(seq 1 22) X Y MT; do
if [ -f chr$c.merged.hm ]; then
        echo chr$c.merged.hm
        tail -n+2 chr$c.merged.hm >> harmonised.tsv
fi
done
