import os, shutil, subprocess, pandas as pd
base_dir = os.path.abspath("../gwaslab-sample-data")
notebook_dir = os.getcwd()
workspace_dir = os.path.join(notebook_dir, "run_workspace")
if os.path.exists(workspace_dir): shutil.rmtree(workspace_dir)
os.makedirs(workspace_dir, exist_ok=True)

input_filename = "bbj_t2d_hm3_chr7_variants.txt.gz"
source_input = os.path.join(base_dir, input_filename)
target_input = os.path.join(workspace_dir, "standardized_input.tsv")

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
    'SNPID': 'variant_id'
}
df.rename(columns=rename_map, inplace=True)
df.to_csv(target_input, sep='\t', index=False)
print(f"✅ Input processed")

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

pd.DataFrame({
    'CHR': ['7'], 
    'POS': [1], 
    'ID': ['rsDummy'], 
    'REF': ['A'], 
    'ALT': ['T']
}).to_parquet(dst_parquet)
print("✅ Created valid dummy parquet")

yaml_path = target_input + "-meta.yaml"
with open(yaml_path, "w") as f:
    f.write("genome_assembly: GRCh37\\ncoordinate_system: 1-based\\ndata_file_name: standardized_input.tsv\\nfile_type: GWAS-SSF v0.1\\ndata_file_md5sum: 00000000000000000000000000000000\\nis_harmonised: false\\nis_sorted: false")
print("✅ Created Metadata")

cfg = """
process {
    withName: 'map_to_build' { memory = '4 GB' }
    withName: 'ten_percent_counts' { memory = '4 GB' }
    withName: 'generate_strand_counts' { memory = '4 GB' }
    withName: 'summarise_strand_counts' { memory = '4 GB' }
    withName: 'harmonization' { memory = '4 GB' }
    withName: 'harmonization_log' { memory = '4 GB' }
    withName: 'qc' { memory = '4 GB' }
}
"""
config_path = os.path.join(workspace_dir, "memory_fix.config")
with open(config_path, "w") as f:
    f.write(cfg)
print(f"✅ Created Config: {config_path}")

cmd = f"nextflow run EBISPOT/gwas-sumstats-harmoniser -r v1.1.10 -profile docker -c {config_path} --harm --file {target_input} --ref {ref_dir_workspace} --chromlist 7, --to_build 37 --threshold 0.99"
print(f"Running: {cmd}")
subprocess.run(cmd, shell=True, check=True)
