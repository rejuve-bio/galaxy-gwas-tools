# import sys
# import subprocess

# # Try importing pysusie; if missing, install from GitHub
# try:
#     import pysusie
# except ImportError:
#     print("pysusie not found. Installing from GitHub...", flush=True)
#     subprocess.check_call([
#         sys.executable, "-m", "pip", "install",
#         "git+https://github.com/stephenslab/pySuSiE.git"
#     ])
#     import pysusie  # retry import after install


# import pandas as pd
# import numpy as np
# import argparse
# import gzip

# # --- Function to handle plain or gzipped files ---
# def read_table_auto(path, **kwargs):
#     if str(path).endswith(".gz"):
#         return pd.read_csv(path, compression="gzip", **kwargs)
#     else:
#         return pd.read_csv(path, **kwargs)

# # --- CLI arguments ---
# parser = argparse.ArgumentParser(description="Run PySuSiE fine-mapping")
# parser.add_argument("--sumstats", required=True, help="Summary statistics file")
# parser.add_argument("--ld_matrix", required=True, help="LD matrix file")
# parser.add_argument("--snp_list", required=True, help="SNP list file")
# parser.add_argument("--n", type=int, required=True, help="GWAS sample size")
# parser.add_argument("--output_creds", required=True, help="Output file for credible sets")
# parser.add_argument("--output_pips", required=True, help="Output file for PIPs")
# args = parser.parse_args()

# # --- Load inputs ---
# sumstats = read_table_auto(args.sumstats, sep="\t")
# ld_matrix = read_table_auto(args.ld_matrix, sep="\t").values
# snp_list = read_table_auto(args.snp_list, sep="\t")["SNP"].tolist()

# # --- Run PySuSiE ---
# result = pysusie.susie_rss(
#     betahat=sumstats["BETA"].values,
#     se=sumstats["SE"].values,
#     R=ld_matrix,
#     n=args.n
# )

# # --- Save outputs ---
# pd.DataFrame(result["sets"]).to_csv(args.output_creds, sep="\t", index=False)
# pd.DataFrame({
#     "SNP": snp_list,
#     "PIP": result["pip"]
# }).to_csv(args.output_pips, sep="\t", index=False)





# import sys
# import subprocess
# import argparse
# import pandas as pd
# import numpy as np

# # --- Auto-install pysusie from GitHub if missing ---
# try:
#     import pysusie
# except ImportError:
#     print("pysusie not found. Installing from GitHub...", flush=True)
#     subprocess.check_call([
#         sys.executable, "-m", "pip", "install",
#         "git+https://github.com/stephenslab/pySuSiE.git"
#     ])
#     import pysusie

# # --- Argument parsing ---
# parser = argparse.ArgumentParser(description="Run PySuSiE fine-mapping")
# parser.add_argument("--sumstats", required=True, help="Path to summary statistics file")
# parser.add_argument("--ld_matrix", required=True, help="Path to LD matrix file")
# parser.add_argument("--snp_list", required=True, help="Path to SNP list file")
# parser.add_argument("--n", type=int, required=True, help="GWAS sample size")
# parser.add_argument("--output_creds", required=True, help="Output file for credible sets")
# parser.add_argument("--output_pips", required=True, help="Output file for PIPs")
# args = parser.parse_args()

# # --- Load data ---
# sumstats = pd.read_csv(args.sumstats, sep="\t")
# ld_matrix = np.loadtxt(args.ld_matrix)
# snp_list = pd.read_csv(args.snp_list, sep="\t", header=None)[0].tolist()

# # --- Run PySuSiE ---
# res = pysusie.susie_rss(
#     betahat=sumstats["BETA"].values,
#     se=sumstats["SE"].values,
#     R=ld_matrix,
#     n=args.n
# )

# # --- Save outputs ---
# pd.DataFrame(res.get("sets", {}).get("cs", []), columns=["Credible_Set"]).to_csv(
#     args.output_creds, sep="\t", index=False
# )
# pd.DataFrame({"SNP": snp_list, "PIP": res.get("pip", [])}).to_csv(
#     args.output_pips, sep="\t", index=False
# )








import sys
import subprocess
import argparse
import pandas as pd
import numpy as np
import time

# --- Auto-install pysusie from GitHub if missing ---
try:
    import pysusie
except ImportError:
    print("pysusie not found. Installing from GitHub...", flush=True)
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "git+https://github.com/stephenslab/pySuSiE.git"
    ])
    import pysusie

# --- Argument parsing ---
parser = argparse.ArgumentParser(description="Run PySuSiE fine-mapping")
parser.add_argument("--sumstats", required=True, help="Path to summary statistics file")
parser.add_argument("--ld_matrix", required=True, help="Path to LD matrix file")
parser.add_argument("--snp_list", required=True, help="Path to SNP list file")
parser.add_argument("--n", type=int, required=True, help="GWAS sample size")
parser.add_argument("--output_creds", required=True, help="Output file for credible sets")
parser.add_argument("--output_pips", required=True, help="Output file for PIPs")
args = parser.parse_args()

print("Loading data...", flush=True)
sumstats = pd.read_csv(args.sumstats, sep="\t")
ld_matrix = np.loadtxt(args.ld_matrix)
snp_list = pd.read_csv(args.snp_list, sep="\t", header=None)[0].tolist()
print(f"Summary stats: {sumstats.shape[0]} SNPs")
print(f"LD matrix shape: {ld_matrix.shape}")
print(f"SNP list length: {len(snp_list)}")

print("Running PySuSiE fine-mapping...", flush=True)
start = time.time()

res = pysusie.susie_rss(
    betahat=sumstats["BETA"].values,
    se=sumstats["SE"].values,
    R=ld_matrix,
    n=args.n,
    L=10,           # limit number of causal signals to speed up
    max_iter=100,  # reduce max iterations
)

print(f"PySuSiE finished in {time.time() - start:.2f} seconds", flush=True)

print("Saving outputs...", flush=True)
pd.DataFrame(res.get("sets", {}).get("cs", []), columns=["Credible_Set"]).to_csv(
    args.output_creds, sep="\t", index=False
)
pd.DataFrame({"SNP": snp_list, "PIP": res.get("pip", [])}).to_csv(
    args.output_pips, sep="\t", index=False
)

print("Done.", flush=True)
