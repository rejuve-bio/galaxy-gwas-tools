import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--genes_raw', required=True)
    parser.add_argument('--set_annot', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    try:
        prefix = 'magma_output'
        cmd = [
            'magma', '--gene-results', args.genes_raw,
            '--set-annot', args.set_annot,
            '--out', prefix
        ]
        subprocess.check_call(cmd)
        # Assuming output is .gsa.out; adjust if .sets.gs
        os.rename(f'{prefix}.gsa.out', args.output)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()