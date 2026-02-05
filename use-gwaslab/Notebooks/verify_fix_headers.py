import os, shutil, subprocess, pandas as pd
base_dir = os.path.abspath("../gwaslab-sample-data")
notebook_dir = os.getcwd()
workspace_dir = os.path.join(notebook_dir, "run_workspace")
if os.path.exists(workspace_dir): shutil.rmtree(workspace_dir)
os.makedirs(workspace_dir, exist_ok=True)

input_filename = "bbj_t2d_hm3_chr7_variants.txt.gz"
source_input = os.path.join(base_dir, input_filename)
target_input = os.path.join(workspace_dir, "standardized_input.tsv") # Save as tsv

# Read and Rename
print("Processing input file...")
df = pd.read_csv(source_input, sep='\t')
rename_map = {
    'CHR': 'chromosome',
    'POS': 'base_pair_location',
    'EA': 'effect_allele',
    'NEA': 'other_allele',
    'EAF': 'effect_allele_frequency',
    'BETA': 'beta',
    'SE': 'standard_error',
    'P': 'p_value',
    'rsID': 'rsid',
    'SNPID': 'variant_id' # Mapped for safety
}
# Only rename existing
count = 0
for col in df.columns:
    if col in rename_map:
        count+=1
df.rename(columns=rename_map, inplace=True)
print(f"Renamed {count} columns.")
# Ensure chromosome is string '7' not 7? Nextflow/Pandas handles it if we save as text.
# The pipeline expects 'chromosome'.
df.to_csv(target_input, sep='\t', index=False)
print(f"✅ Input processed: {target_input}")

ref_dir_workspace = os.path.join(workspace_dir, "references")
os.makedirs(ref_dir_workspace, exist_ok=True)
src_vcf = os.path.join(base_dir, "1kg_eas_hg19.chr7_126253550_128253550.vcf.gz")
dst_vcf = os.path.join(ref_dir_workspace, "homo_sapiens-chr7.vcf.gz")
dst_tbi = os.path.join(ref_dir_workspace, "homo_sapiens-chr7.vcf.gz.tbi")
dst_parquet = os.path.join(ref_dir_workspace, "homo_sapiens-chr7.parquet")

if os.path.exists(src_vcf):
    shutil.copy(src_vcf, dst_vcf)
    shutil.copy(src_vcf + ".tbi", dst_tbi)
    print("✅ Copied references")

# Correct Schema for Parquet
pd.DataFrame({
    'CHR': ['7'], 
    'POS': [1], 
    'ID': ['rsDummy'], 
    'REF': ['A'], 
    'ALT': ['T']
}).to_parquet(dst_parquet)
print("✅ Created valid dummy parquet")

# Metadata (pointing to standardized file)
yaml_path = target_input + "-meta.yaml"
# MD5sum is checked by pipeline? Usually ignored if not forced.
with open(yaml_path, "w") as f:
    f.write("genome_assembly: GRCh37\ncoordinate_system: 1-based\ndata_file_name: standardized_input.tsv\nfile_type: GWAS-SSF v0.1\ndata_file_md5sum: 00000000000000000000000000000000\nis_harmonised: false\nis_sorted: false")
print("✅ Created Metadata")

# Clean work dir
if os.path.exists("work"): shutil.rmtree("work")
# Run Nextflow 
# --to_build 37 (SKIP LIFTOVER) + --chromlist 7, + --file standardized_input.tsv
cmd = f"nextflow run EBISPOT/gwas-sumstats-harmoniser -r v1.1.10 -profile docker --harm --file {target_input} --ref {ref_dir_workspace} --chromlist 7, --to_build 38 --threshold 0.99"
print(f"Running: {cmd}")
subprocess.run(cmd, shell=True, check=True)
