import argparse
import subprocess
import sys
import os

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
        prefix = 'magma_output'
        cmd = [
            'magma', '--bfile', args.bfile,
            '--pval', args.pval_file, f'N={args.N}',
            '--gene-annot', args.genes_annot,
            '--out', prefix
        ]
        subprocess.check_call(cmd)
        os.rename(f'{prefix}.genes.raw', 'genes.raw')
        os.rename(f'{prefix}.genes.out', 'genes.out')
        os.rename('genes.raw', args.genes_raw_out)
        os.rename('genes.out', args.genes_out_out)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()