# import argparse
# import rpy2.robjects as ro
# from rpy2.robjects.packages import importr

# parser = argparse.ArgumentParser()
# parser.add_argument('--input', required=True)
# parser.add_argument('--output', required=True)
# args = parser.parse_args()

# mungesumstats = importr('MungeSumstats')
# mungesumstats.format_sumstats(
#     path=args.input,
#     ref_genome="GRCh37",
#     save_path=args.output,
#     drop_indels=True,
#     save_format="LDSC"
# )




import argparse
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import os
import tempfile
import shutil

# Parse Galaxy paths
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

# Generate a temp file with valid extension for MungeSumstats
tmp_output = tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name

# Run MungeSumstats using the temporary path
mungesumstats = importr('MungeSumstats')
mungesumstats.format_sumstats(
    path=args.input,
    ref_genome="GRCh37",
    save_path=tmp_output,
    drop_indels=True,
    save_format="LDSC"
)

# Move temp output to Galaxy's final destination
shutil.move(tmp_output, args.output)
