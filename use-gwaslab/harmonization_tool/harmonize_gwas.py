import argparse
import gwaslab as gl
import logging
import os

# Parse arguments
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
logging.info("GWASLab Harmonization Tool started")

# Download rsID if keyword provided
if args.ref_rsid_tsv_keyword:
    gl.download_ref(args.ref_rsid_tsv_keyword)
    args.ref_rsid_tsv = gl.get_path(args.ref_rsid_tsv_keyword)

# Load with manual columns if provided
load_kwargs = {}
if args.snpid: load_kwargs['snpid'] = args.snpid
if args.chrom: load_kwargs['chrom'] = args.chrom
if args.pos: load_kwargs['pos'] = args.pos
if args.ea: load_kwargs['ea'] = args.ea
if args.nea: load_kwargs['nea'] = args.nea
if args.eaf: load_kwargs['neaf'] = args.eaf  # GWASLab uses neaf for EAF
if args.beta: load_kwargs['beta'] = args.beta
if args.se: load_kwargs['se'] = args.se
if args.p: load_kwargs['p'] = args.p
if args.n: load_kwargs['n'] = args.n

logging.info("Loading sumstats")
ss = gl.Sumstats(args.input, fmt=args.format, **load_kwargs)

# Infer build
ss.infer_build()
build = ss.meta.get('genome_build', 'unknown')
logging.info(f"Build detected/inferred: {build}")

# QC
logging.info("Running basic_check")
ss.basic_check(remove_dup=True, threads=4)

# rsID annotation if provided
if args.ref_rsid_tsv:
    logging.info("Annotating rsIDs")
    ss.assign_rsid2(path=args.ref_rsid_tsv, threads=4, overwrite="all")

# Harmonize (references are mandatory)
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

# Save
logging.info("Saving harmonized output")
ss.to_format(args.output[:-7], fmt="ldsc", hapmap3=True, exclude_hla=True, md5sum=True)

logging.info("Tool finished successfully")