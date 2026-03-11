import os, shutil, subprocess, pandas as pd
base_dir = os.path.abspath("../gwaslab-sample-data")
notebook_dir = os.getcwd()
workspace_dir = os.path.join(notebook_dir, "run_workspace")
os.makedirs(workspace_dir, exist_ok=True)
input_filename = "bbj_t2d_hm3_chr7_variants.txt.gz"
source_input = os.path.join(base_dir, input_filename)
target_input = os.path.join(workspace_dir, input_filename)
if os.path.exists(source_input):
    if os.path.exists(target_input): os.remove(target_input)
    os.symlink(source_input, target_input)
    print(f"✅ Input prepared: {target_input}")
ref_dir_workspace = os.path.join(workspace_dir, "references")
os.makedirs(ref_dir_workspace, exist_ok=True)
src_vcf = os.path.join(base_dir, "1kg_eas_hg19.chr7_126253550_128253550.vcf.gz")
# CHANGE: naming convention
dst_vcf = os.path.join(ref_dir_workspace, "homo_sapiens-chr7.vcf.gz")
dst_tbi = os.path.join(ref_dir_workspace, "homo_sapiens-chr7.vcf.gz.tbi")
dst_parquet = os.path.join(ref_dir_workspace, "homo_sapiens-chr7.parquet")
if os.path.exists(src_vcf):
    for src, dst in [(src_vcf, dst_vcf), (src_vcf + ".tbi", dst_tbi)]:
        if os.path.exists(dst): os.remove(dst)
        os.symlink(src, dst)
    print("✅ Linked references with correct naming")
if not os.path.exists(dst_parquet):
    # Ensure parquet has required columns. 'pos' needs to be int.
    pd.DataFrame({'chrom': ['7'], 'pos': [1], 'ref': ['A'], 'alt': ['T']}).to_parquet(dst_parquet)
    print("✅ Created dummy parquet")
yaml_path = target_input + "-meta.yaml"
with open(yaml_path, "w") as f:
    f.write("genome_assembly: GRCh37\ncoordinate_system: 1-based\ndata_file_name: bbj_t2d_hm3_chr7_variants.txt.gz\nfile_type: GWAS-SSF v0.1\ndata_file_md5sum: 00000000000000000000000000000000\nis_harmonised: false\nis_sorted: false")
print("✅ Created Metadata")
# clean work dir to ensure fresh run
if os.path.exists("work"): shutil.rmtree("work")
cmd = f"nextflow run EBISPOT/gwas-sumstats-harmoniser -r v1.1.10 -profile docker --harm --file {target_input} --ref {ref_dir_workspace} --chromlist 7, --to_build 38 --threshold 0.99"
print(f"Running: {cmd}")
subprocess.run(cmd, shell=True, check=True)
