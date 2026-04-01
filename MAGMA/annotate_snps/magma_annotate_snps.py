import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snp_loc', required=True)
    parser.add_argument('--gene_loc', required=True)
    parser.add_argument('--window_upstream', required=True)
    parser.add_argument('--window_downstream', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    try:
        prefix = 'magma_output'
        cmd = [
            'magma', '--annotate', f'window={args.window_upstream},{args.window_downstream}',
            '--snp-loc', args.snp_loc,
            '--gene-loc', args.gene_loc,
            '--out', prefix
        ]
        subprocess.check_call(cmd)
        os.rename(f'{prefix}.genes.annot', args.output)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()