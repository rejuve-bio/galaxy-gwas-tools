import argparse
import gwaslab as gl
import logging
import os

# Parse Galaxy arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--format', default='auto')
parser.add_argument('--snpid_col', default=None)
parser.add_argument('--chrom_col', default=None)
parser.add_argument('--pos_col', default=None)
parser.add_argument('--ea_col', default=None)
parser.add_argument('--nea_col', default=None)
parser.add_argument('--eaf_col', default=None)
parser.add_argument('--beta_col', default=None)
parser.add_argument('--se_col', default=None)
parser.add_argument('--p_col', default=None)
parser.add_argument('--n_col', default=None)
parser.add_argument('--ref_seq', default=None)
parser.add_argument('--ref_seq_keyword', default=None)
parser.add_argument('--ref_infer', default=None)
parser.add_argument('--ref_infer_keyword', default=None)
parser.add_argument('--ref_rsid_tsv', default=None)
parser.add_argument('--ref_rsid_tsv_keyword', default=None)
parser.add_argument('--output', required=True)
parser.add_argument('--log', required=True)
args = parser.parse_args()

# Setup logging
logging.basicConfig(filename=args.log, level=logging.INFO, format='%(asctime)s %(message)s')
logging.info("Tool started")

# Download if keywords provided
if args.ref_seq_keyword:
    gl.download_ref(args.ref_seq_keyword)
    args.ref_seq = gl.get_path(args.ref_seq_keyword)
if args.ref_infer_keyword:
    gl.download_ref(args.ref_infer_keyword)
    args.ref_infer = gl.get_path(args.ref_infer_keyword)
if args.ref_rsid_tsv_keyword:
    gl.download_ref(args.ref_rsid_tsv_keyword)
    args.ref_rsid_tsv = gl.get_path(args.ref_rsid_tsv_keyword)

# Load with column mappings if provided
load_kwargs = {}
if args.snpid_col: load_kwargs['snpid'] = args.snpid_col
if args.chrom_col: load_kwargs['chrom'] = args.chrom_col
if args.pos_col: load_kwargs['pos'] = args.pos_col
if args.ea_col: load_kwargs['ea'] = args.ea_col
if args.nea_col: load_kwargs['nea'] = args.nea_col
if args.eaf_col: load_kwargs['neaf'] = args.eaf_col  # neaf for EAF in GWASLab
if args.beta_col: load_kwargs['beta'] = args.beta_col
if args.se_col: load_kwargs['se'] = args.se_col
if args.p_col: load_kwargs['p'] = args.p_col
if args.n_col: load_kwargs['n'] = args.n_col

logging.info("Loading sumstats")
ss = gl.Sumstats(args.input, fmt=args.format, **load_kwargs)

# Infer build if unknown
ss.infer_build()
build = ss.meta.get('genome_build', 'unknown')
build_short = '19' if '19' in str(build).lower() else '38'
logging.info(f"Build: {build}")

# QC
logging.info("QC")
ss.basic_check(remove_dup=True, threads=4)

# rsID if provided
if args.ref_rsid_tsv:
    logging.info("Annotating rsIDs")
    ss.assign_rsid2(path=args.ref_rsid_tsv, threads=4, overwrite="all")

# Harmonize if references provided
if args.ref_seq or args.ref_infer:
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

# Save output
logging.info("Saving")
ss.to_format(args.output[:-7], fmt="ldsc", hapmap3=True, exclude_hla=True, md5sum=True)  # Remove .gz for base name

logging.info("Tool finished")