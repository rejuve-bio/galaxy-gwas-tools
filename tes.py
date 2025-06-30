import marimo

__generated_with = "0.13.15"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""### Munge Sumstats Data""")
    return


@app.cell
def _(RRuntimeError):
    import rpy2.robjects as ro
    from rpy2.robjects.packages import importr
    from rpy2.robjects import pandas2ri
    import os # For path manipulation if needed

    # Activate the pandas to R data frame conversion
    # pandas2ri.activate()

    # Import R's base and utils packages
    base = importr('base')
    utils = importr('utils')


    try:
        mungesumstats = importr('MungeSumstats')
    except RRuntimeError as e:
        print(f"Error importing MungeSumstats: {e}")
        print("Please ensure MungeSumstats is installed in your R environment.")
        print("You can install it in R using: BiocManager::install('MungeSumstats')")
        exit()


    sumstats_file = "./data/raw/21001_raw.gwas.imputed_v3.both_sexes.tsv.bgz" 

    ref_genome = "GRCh37" 
    output_path = "./data/raw/21001_munged.gwas.imputed_v3.both_sexes.tsv" 

    try:
        formatted_file_path_r = mungesumstats.format_sumstats(
            path=sumstats_file,
            ref_genome=ref_genome,
            save_path=output_path,
            drop_indels=True,
            nThread=14,
            log_folder="./data/logs",
            log_mungesumstats_msgs=True,
            save_format="LDSC",
            # force_new=True
        )

        formatted_file_path_py = list(formatted_file_path_r)[0]

        print(f"MungeSumstats successfully formatted the file.")
        print(f"Formatted file saved at: {formatted_file_path_py}")


    except Exception as e:
        print(f"An error occurred while running MungeSumstats format_sumstats: {e}")
        print("Please check the MungeSumstats documentation and your input file.")
    return os, output_path


@app.cell
def _(output_path):
    import pandas as pd
    import numpy as np
    # Load the munged sumstats file into a pandas DataFrame
    munged_df = pd.read_csv(output_path, sep='\t', low_memory=False)
    print(f"Loaded munged sumstats file with {munged_df.shape[0]} rows and {munged_df.shape[1]} columns.")
    # Display the first few rows of the munged DataFrame
    munged_df["ID"] = munged_df["CHR"].astype(str) + ":" + munged_df["BP"].astype(str) + ":" + munged_df["A2"] + ":" + munged_df["A1"]
    # Set it as an index
    munged_df.reset_index()
    munged_df.set_index(["ID"], inplace=True)
    munged_df.to_csv(output_path, sep='\t', index=False)
    munged_df.head()
    return munged_df, np, pd


@app.cell
def _(munged_df):
    # Keep only SNPs with p-value < 5e-8
    significant_snps_df = munged_df[munged_df['P'] < 5e-8]
    print(f"Filtered significant SNPs with p-value < 5e-8: {significant_snps_df.shape[0]} rows.")

    # save 
    significant_snps_df.to_csv("./data/raw/21001_munged.gwas.imputed_v3.both_sexes_sig.tsv", index=False)
    return (significant_snps_df,)


@app.cell
def _(mo):
    mo.md(r"""### Download 1000G vcf files for chr1-22""")
    return


@app.cell
def _():
    import subprocess as sp

    scripts = [
        # "./scripts/1000Genomes_phase3/1_download_vcfs.sh",
        # "./scripts/1000Genomes_phase3/2_normalise_vcfs.sh",
        # "./scripts/1000Genomes_phase3/3_make_population_ids.sh",
        # "./scripts/1000Genomes_phase3/4_convert_to_plink.sh"
    ]

    output_dir = "./data/1000Genomes_phase3"

    for script in scripts:
        print(f"Running script: {script}")
        result = sp.run(["bash", script, output_dir], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running {script}: {result.stderr}")
        else:
            print(f"Successfully ran {script}: {result.stdout}")

    print("All scripts executed successfully.")
    return (sp,)


@app.cell
def _(mo):
    mo.md(r"""### GCTA COJO Analysis for each chr""")
    return


@app.cell
def _(os, pd, sp):
    import tempfile

    def run_gcta_cojo_analysis(sumstats_file: pd.DataFrame, 
                               plink_dir: str, 
                               maf: float, 
                               population: str) -> pd.DataFrame:
        """
        Run GCTA COJO analysis on the given summary statistics file.
    
        Parameters:
        - sumstats_file: Path to the summary statistics file.
        - plink_dir: Directory containing PLINK files.
        - maf: Minor allele frequency threshold.
        - population: Population for which the analysis is run.
        """

        # Add and ID column with chr:bp:ref:alt consistent with plink
        cojo_df = sumstats_file[["A1", "A2", "FRQ", "BETA", "SE", "P", "N"]].copy()
        cojo_df["SNP"] = sumstats_file.index
        # Move SNP column to the front
        cojo_df = cojo_df[['SNP', 'A1', 'A2', 'FRQ', 'BETA', 'SE', 'P', 'N']]

        # Create temp directory for COJO results
        with tempfile.TemporaryDirectory() as gcta_out_dir:
        # gcta_out_dir = "./data/gcta_cojo_results"
        # if not os.path.exists(gcta_out_dir):
        #     os.makedirs(gcta_out_dir)
            cojo_sumstats_file_path = os.path.join(gcta_out_dir, "cojo_sumstats.txt")
            cojo_df.to_csv(cojo_sumstats_file_path, sep='\t', index=False)
        
            gcta_cojo_script = "./scripts/6_gcta_cojo_analysis.sh"
            # Run GCTA COJO analysis
            gcta_cojo_cmd = [
                "bash", gcta_cojo_script, 
                  gcta_out_dir,
                  plink_dir,
                  cojo_sumstats_file_path,
                  str(maf),
                  population
            ]
        
            print(f"Running GCTA COJO command: {' '.join(gcta_cojo_cmd)}")
            gcta_cojo_result = sp.run(gcta_cojo_cmd, capture_output=True, text=True)
            if gcta_cojo_result.returncode != 0:
                print(f"Error running GCTA COJO: {gcta_cojo_result.stderr}")
            else:
                print(f"Successfully ran GCTA COJO: {gcta_cojo_result.stdout}")
                print(f"Results saved to {gcta_out_dir}")
    
            # Read the combined results   
            # Merge COJO files
            combined_cojo_res = []
            for i in range(1, 23):
                cojo_result_file = f"{gcta_out_dir}/{population}.{i}.cojo_sumstats.txt.maf.{maf}.jma.cojo"
                if os.path.exists(cojo_result_file):
                    cojo_df_tmp = pd.read_csv(cojo_result_file, sep='\t', low_memory=False)
                    combined_cojo_res.append(cojo_df_tmp)
                else:
                    print(f"File {cojo_result_file} does not exist. Skipping.")
        
            combined_cojo_df = pd.concat(combined_cojo_res, ignore_index=True, axis=0)
            combined_cojo_df.rename(columns={"SNP": "ID"}, inplace=True)
            # Set the SNP column as index
            combined_cojo_df.reset_index()
            combined_cojo_df.set_index('ID', inplace=True)
            combined_cojo_df.drop_duplicates()
            # combined_cojo_df.to_csv(combined_cojo_file_path, sep='\t', index=True)
            print(f"Combined COJO: {combined_cojo_df.shape}")
            return combined_cojo_df
    return (run_gcta_cojo_analysis,)


app._unparsable_cell(
    r"""
    from rpy2.robjects import numpy2ri, r
    import optuna 
    from typing import Tuple, Any

    def calculate_ld_for_region(sumstats: pd.DataFrame, chr: int, position: int, window: int = 500, population: str = \"EUR\") -> pd.DataFrame:
        # window size is in kb
        window = window * 1000
       # Filter the sumstats data for all snps around the posion
        start = position - window
        end = position + window
        filtered_region = sumstats[(sumstats[\"CHR\"] == chr) &
                                    (sumstats[\"BP\"] >= start) &
                                    (sumstats[\"BP\"] <= end)]
    
        filtered_ids = filtered_region.index.tolist()
        print(f\"Filtered {len(filtered_ids)} SNPs in the region around position {position} on chromosome {chr}.\")
        # Create a temporary file to store the IDs and use tmp file for ld
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp_file:
            for snp_id in filtered_ids:
                tmp_file.write(f\"{snp_id}\n\")
            tmp_file_path = tmp_file.name
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp_file_ld:
                tmp_file_ld_path = tmp_file_ld.name
                plink_cmd = [
                    \"plink2\",
                    \"--bfile\", f\"{plink_dir}/{population}/{population}.{chr}.1000Gp3.20130502\",
                    \"--keep-allele-order\",
                    \"--r-unphased\", \"square\",
                    \"--extract\", tmp_file_path,
                    \"--out\", tmp_file_ld_path
                ]
                # Join and print as a single command
                print(f\"Running PLINK command: {' '.join(plink_cmd)}\")
                ld_run_res = sp.run(plink_cmd, capture_output=True, text=True)
                if ld_run_res.returncode != 0:
                    print(f\"Error running PLINK for LD calculation: {ld_run_res.stderr}\")
                    return None
                ld_out_path = f\"{tmp_file_ld_path}.unphased.vcor1\"
                print(f\"LD output file path: {ld_out_path}\")
                ld_vars_path = f\"{ld_out_path}.vars\"
                # read the vars file to get the SNPs
                snp_ids = []
                with open(ld_vars_path, 'r') as f:
                    for line in f:
                        snp_ids.append(line.strip())
            
                ld_df = pd.read_csv(ld_out_path, sep='\t', header=None)
                ld_df.index = snp_ids
                ld_df.fillna(0, inplace=True)
                #Clean up temporary files
                os.remove(tmp_file_path)
                os.remove(tmp_file_ld_path)
                os.remove(ld_out_path)
                os.remove(f\"{ld_out_path}.vars\")

                return ld_df
            
    def objective_susie(trial, seed, susieR, zhat, R, num_samples):

        L = trial.suggest_int(\"L\", 1, 20)
        susie_fit = susieR.susie_rss(
                        # bhat = bhat_r,
                        # shat = shat_r,
                        z = zhat,
                        R = R,
                        L = L,
                        n = num_samples
                    )
        # elbox_index = list(susie_fit.names()).index('elbo')
        elbo = susie_fit.rx2('elbo')[-1]
        converged = susie_fit.rx2('converged')[0]
        print(f\"Converged status: {converged}\")
        if converged == 1:
            print(f\"Running with L = {L}. Converged with ELBO {elbo}\")
            return elbo

        return -np.inf

    def finemap_region(seed: int, sumstats: pd.DataFrame, chr: int, lead_variant_position: str, window: int, population: str = \"EUR\", L: int = 5, coverage: float = 0.95, min_abs_corr: float = 0.5) -> Tuple[Any]:

        ld_df = calculate_ld_for_region(sumstats, chr, lead_variant_position, 
                                   window)
        sub_region_sumstats_ld = sumstats.loc[ld_df.index]
        print(f\"Sub-region sumstats shape after filtering by LD: {sub_region_sumstats_ld.shape}\")
        num_samples = int(sub_region_sumstats_ld[\"N\"].iloc[0])
        try:
            susieR = importr('susieR')

            ro.r(f'set.seed({seed})')
            zhat = sub_region_sumstats_ld[\"Z\"].values.reshape(len(ld_df), 1)
            LD_mat = ld_df.values
        
            with (ro.default_converter + numpy2ri.converter).context():
                # Enable conversion between numpy arrays and R matrices
                zhat_r  = ro.conversion.get_conversion().py2rpy(zhat)
                R_r  = ro.conversion.get_conversion().py2rpy(LD_mat)
    
            if L <= 0: # Do hyper-paramter search
                study = optuna.create_study(direction=\"maximize\")
                study.optimize(lambda trial: objective_susie(trial, seed, susieR, zhat_r, R_r, num_samples), n_trials=10)
                L = study.best_params[\"L\"]
                print(f\"Best L found: {L} with ELBO {study.best_value}\")
                susie_fit = susieR.susie_rss(
                    z=zhat_r,
                    R=R_r,
                    L=L,
                    n=num_samples)

            else:
                susie_fit = susieR.susie_rss(
                    z=zhat_r,
                    R=R_r,
                    L=L,
                    n=num_samples)

            credible_sets = susieR.susie_get_cs(susie_fit, coverage=coverage, min_abs_corr=min_abs_corr, Xcorr=R_r)
            pips = susieR.susie_get_pip(susie_fit)
            sub_region_sumstats_ld[\"PIP\"] = pips
            print(f\"Credible sets found: {len(credible_sets[0])}\")
            return susie_fit, sub_region_sumstats_ld, credible_sets
        except RuntimeError as e:
            print(f\"Error importing susieR: {e}\")
            print(\"Please ensure MungeSumstats is installed in your R environment.\")
            exit()

    def finemap_cojo_result(seed: int, sumstats: pd.DataFrame,)
    """,
    name="_"
)


@app.cell
def _(run_gcta_cojo_analysis, significant_snps_df):
    # Convert the summary statistis data to COJO format
    plink_dir = "./data/1000Genomes_phase3/plink_format_b37"
    maf = 0.01
    population = "EUR"
    combined_cojo_df = run_gcta_cojo_analysis(significant_snps_df,
                                               plink_dir,
                                               maf,
                                               population)
    # Display the combined COJO results
    combined_cojo_df.head()
    return


@app.cell
def _(finemap_region, munged_df):
    variant_position = 53802494
    chr_ = 16
    susie_fit_res, sub_region_sumstats_ld, credible_sets = finemap_region(
        seed=42,
        sumstats=munged_df,
        chr=chr_,
        lead_variant_position=variant_position,
        window=2000,
        population="EUR",
        L=-1, 
        coverage=0.95,
        min_abs_corr=0.5
    )
    return credible_sets, sub_region_sumstats_ld


@app.cell
def _(credible_sets):
    print(credible_sets[0])
    return


@app.cell
def _(credible_sets, np, sub_region_sumstats_ld):
    cs_index = list(np.array(credible_sets[0]).squeeze() - 1)
    sub_region_sumstats_ld.iloc[cs_index]
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()