import argparse
import gwaslab as gl
import logging
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help="GWAS summary statistics file")
parser.add_argument('--format', default='auto', help="Format keyword or 'manual'")
parser.add_argument('--snpid', default=None, help="SNPID column name")
parser.add_argument('--chrom', default=None, help="CHR column name")
parser.add_argument('--pos', default=None, help="POS column name")
parser.add_argument('--ea', default=None, help="EA column name")
parser.add_argument('--nea', default=None, help="NEA column name")
parser.add_argument('--eaf', default=None, help="EAF column name")
parser.add_argument('--beta', default=None, help="BETA column name")
parser.add_argument('--se', default=None, help="SE column name")
parser.add_argument('--p', default=None, help="P column name")
parser.add_argument('--n', default=None, help="N column name")
parser.add_argument('--ref_seq', required=True, help="Reference genome FASTA file (uploaded)")
parser.add_argument('--ref_infer', required=True, help="Inference VCF file with AF (uploaded)")
parser.add_argument('--ref_rsid_tsv', default=None, help="rsID TSV file (optional, uploaded)")
parser.add_argument('--output', required=True, help="Output base name")
parser.add_argument('--log', required=True, help="Log file")
args = parser.parse_args()

# Logging
logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s %(message)s')
logging.info("GWASLab Harmonization Tool started")

# Load kwargs for manual columns if provided
load_kwargs = {}
for k, v in vars(args).items():
    if k in ['snpid', 'chrom', 'pos', 'ea', 'nea', 'eaf', 'beta', 'se', 'p', 'n'] and v:
        load_kwargs[k] = v

logging.info("Loading sumstats")
ss = gl.Sumstats(args.input, fmt=args.format, **load_kwargs)

ss.infer_build()
build = ss.meta.get('genome_build', 'unknown')
logging.info(f"Build detected/inferred: {build}")

logging.info("Running basic_check")
ss.basic_check(remove_dup=True, threads=4)

if args.ref_rsid_tsv:
    logging.info("Annotating rsIDs")
    ss.assign_rsid2(path=args.ref_rsid_tsv, threads=4, overwrite="all")
else:
    logging.info("Skipping rsID annotation")

logging.info("Harmonizing")
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

logging.info("Saving harmonized output")
ss.to_format(args.output[:-3], fmt="ldsc", hapmap3=True, exclude_hla=True, md5sum=True)  # .gz handled by Galaxy

logging.info("Finished successfully")