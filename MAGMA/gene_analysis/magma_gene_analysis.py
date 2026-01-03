import argparse
import subprocess
import sys
import os
import time
import glob
import shutil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bfile', required=True)
    parser.add_argument('--pval_file', required=True)
    parser.add_argument('--N', required=True)
    parser.add_argument('--genes_annot', required=True)
    parser.add_argument('--genes_raw_out', required=True)
    parser.add_argument('--genes_out_out', required=True)
    args = parser.parse_args()

    try:
        # Unique prefix based on timestamp
        timestamp = int(time.time())
        prefix = f'magma_gene_analysis_{timestamp}'

        # Aggressive cleanup: remove any old MAGMA output files starting with "magma_"
        for pattern in ['magma_*', 'genes.raw', 'genes.out', '*.log']:
            for file in glob.glob(pattern):
                try:
                    if os.path.isfile(file):
                        os.remove(file)
                    elif os.path.isdir(file):
                        shutil.rmtree(file)
                except Exception as e:
                    sys.stderr.write(f"Warning: Could not remove {file}: {e}\n")

        sys.stderr.write(f"Starting MAGMA gene analysis at {time.ctime()}\n")

        cmd = [
            'magma',
            '--bfile', args.bfile,
            '--pval', args.pval_file, f'N={args.N}',
            '--gene-annot', args.genes_annot,
            '--out', prefix
        ]

        # Optional: reduce memory and speed up (recommended for testing)
        # cmd += ['--model', 'snp-wise=mean']  # default, but explicit
        # cmd += ['--settings', 'no-corr']  # disables gene-gene correlations → much faster, less memory

        subprocess.check_call(cmd)

        # Copy final outputs
        os.rename(f'{prefix}.genes.raw', args.genes_raw_out)
        os.rename(f'{prefix}.genes.out', args.genes_out_out)

        sys.stderr.write(f"MAGMA completed successfully. Output prefix: {prefix}\n")

    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"MAGMA failed with return code {e.returncode}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()