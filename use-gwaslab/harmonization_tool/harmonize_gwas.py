import argparse
import gwaslab as gl
import logging
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--format', default='auto')
parser.add_argument('--snpid', default=None)
parser.add_argument('--chrom', default=None)
parser.add_argument('--pos', default=None)
parser.add_argument('--ea', default=None)
parser.add_argument('--nea', default=None)
parser.add_argument('--eaf', default=None)
parser.add_argument('--beta', default=None)
parser.add_argument('--se', default=None)
parser.add_argument('--p', default=None)
parser.add_argument('--n', default=None)
parser.add_argument('--ref_seq', required=True)
parser.add_argument('--ref_infer', required=True)
parser.add_argument('--ref_rsid_tsv', default=None)
parser.add_argument('--ref_rsid_tsv_keyword', default=None)
parser.add_argument('--output', required=True)
parser.add_argument('--log', required=True)
args = parser.parse_args()

# Logging
logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s %(message)s')
logging.info("Tool started")

# Handle rsID keyword download
if args.ref_rsid_tsv_keyword:
    gl.download_ref(args.ref_rsid_tsv_keyword)
    args.ref_rsid_tsv = gl.get_path(args.ref_rsid_tsv_keyword)

# Load kwargs for manual columns
load_kwargs = {}
for k, v in vars(args).items():
    if k in ['snpid', 'chrom', 'pos', 'ea', 'nea', 'eaf', 'beta', 'se', 'p', 'n'] and v:
        load_kwargs[k] = v

ss = gl.Sumstats(args.input, fmt=args.format, **load_kwargs)

ss.infer_build()
build = ss.meta.get('genome_build', 'unknown')
logging.info(f"Build: {build}")

ss.basic_check(remove_dup=True, threads=4)

if args.ref_rsid_tsv:
    ss.assign_rsid2(path=args.ref_rsid_tsv, threads=4, overwrite="all")

ss.harmonize(
    basic_check=False,
    ref_seq=args.ref_seq,
    ref_infer=args.ref_infer,
    ref_alt_freq="AF",
    ref_rsid_tsv=args.ref_rsid_tsv,
    threads=4,
    remove=False,
    sweep_mode=True
)
ss.flip_allele_stats()

ss.to_format(args.output[:-3], fmt="ldsc", hapmap3=True, exclude_hla=True, md5sum=True)  # .gz handled by Galaxy

logging.info("Finished")