# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import tempfile
# import shutil
# from pathlib import Path

# def main():
#     parser = argparse.ArgumentParser(description='GWAS Harmonizer Setup Wrapper')
#     parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
#     parser.add_argument('--ref-dir', required=True, help='Reference data directory')
#     parser.add_argument('--chromlist', default='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT',
#                        help='Comma-separated list of chromosomes')
    
#     args = parser.parse_args()
    
#     # Validate inputs
#     if not os.path.isdir(args.code_repo):
#         sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
#     # Create reference directory
#     os.makedirs(args.ref_dir, exist_ok=True)
    
#     # Set up environment
#     env = os.environ.copy()
#     env['PATH'] = f"{args.code_repo}:{env['PATH']}"
    
#     # Create log directory
#     log_dir = os.path.join(args.ref_dir, "logs")
#     os.makedirs(log_dir, exist_ok=True)
    
#     # Build Nextflow command
#     cmd = [
#         'nextflow', 'run', args.code_repo,
#         '-profile', 'standard',
#         '--reference',
#         '--ref', args.ref_dir,
#         '--chromlist', args.chromlist,
#         '-with-report', os.path.join(log_dir, 'ref-report.html'),
#         '-with-timeline', os.path.join(log_dir, 'ref-timeline.html'),
#         '-with-trace', os.path.join(log_dir, 'ref-trace.txt')
#     ]
    
#     # Run Nextflow
#     log_file = os.path.join(log_dir, 'ref.log')
#     try:
#         with open(log_file, 'w') as log_f:
#             process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
#             # Stream output to both console and log file
#             for line in process.stdout:
#                 print(line, end='')
#                 log_f.write(line)
#                 log_f.flush()
            
#             return_code = process.wait()
            
#         if return_code != 0:
#             sys.exit(f"Nextflow process failed with return code: {return_code}")
            
#         # Create output files for Galaxy
#         with open('log_dir.txt', 'w') as f:
#             f.write(log_dir)
            
#         # Copy report files to current directory for Galaxy outputs
#         for report_file in ['ref-report.html', 'ref-timeline.html']:
#             src = os.path.join(log_dir, report_file)
#             if os.path.exists(src):
#                 shutil.copy2(src, '.')
                
#     except Exception as e:
#         sys.exit(f"Error running harmonizer setup: {str(e)}")

# if __name__ == '__main__':
#     main()






# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import shutil
# from pathlib import Path

# def main():
#     parser = argparse.ArgumentParser(description='GWAS Harmonizer Setup Wrapper')
#     parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
#     parser.add_argument('--ref-dir', required=True, help='Reference data directory')
#     parser.add_argument('--chromlist', default='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT',
#                        help='Comma-separated list of chromosomes')
    
#     args = parser.parse_args()
    
#     # Validate inputs
#     if not os.path.isdir(args.code_repo):
#         sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
#     # Create reference directory
#     os.makedirs(args.ref_dir, exist_ok=True)
    
#     # Use absolute path to nextflow
#     nextflow_path = os.path.join(args.code_repo, 'nextflow')
#     if not os.path.exists(nextflow_path):
#         sys.exit(f"Error: Nextflow not found at {nextflow_path}")
    
#     # Set up environment
#     env = os.environ.copy()
#     env['PATH'] = f"{args.code_repo}:{env['PATH']}"
    
#     # Create log directory
#     log_dir = os.path.join(args.ref_dir, "logs")
#     os.makedirs(log_dir, exist_ok=True)
    
#     # Build Nextflow command using absolute path
#     cmd = [
#         nextflow_path, 'run', args.code_repo,
#         '-profile', 'standard',
#         '--reference',
#         '--ref', args.ref_dir,
#         '--chromlist', args.chromlist,
#         '-with-report', os.path.join(log_dir, 'ref-report.html'),
#         '-with-timeline', os.path.join(log_dir, 'ref-timeline.html'),
#         '-with-trace', os.path.join(log_dir, 'ref-trace.txt')
#     ]
    
#     # Run Nextflow
#     log_file = os.path.join(log_dir, 'ref.log')
#     try:
#         with open(log_file, 'w') as log_f:
#             print(f"Running command: {' '.join(cmd)}")
#             print(f"Nextflow path: {nextflow_path}")
#             print(f"Code repo: {args.code_repo}")
            
#             process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
#             # Stream output to both console and log file
#             for line in process.stdout:
#                 print(line, end='')
#                 log_f.write(line)
#                 log_f.flush()
            
#             return_code = process.wait()
            
#         if return_code != 0:
#             sys.exit(f"Nextflow process failed with return code: {return_code}")
            
#         # Create output files for Galaxy
#         with open('log_dir.txt', 'w') as f:
#             f.write(log_dir)
            
#         # Copy report files to current directory for Galaxy outputs
#         for report_file in ['ref-report.html', 'ref-timeline.html']:
#             src = os.path.join(log_dir, report_file)
#             if os.path.exists(src):
#                 shutil.copy2(src, '.')
                
#     except Exception as e:
#         sys.exit(f"Error running harmonizer setup: {str(e)}")

# if __name__ == '__main__':
#     main()






# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# import subprocess
# import shutil
# from pathlib import Path

# def main():
#     parser = argparse.ArgumentParser(description='GWAS Harmonizer Setup Wrapper')
#     parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
#     parser.add_argument('--ref-dir', required=True, help='Reference data directory')
#     parser.add_argument('--chromlist', default='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT',
#                        help='Comma-separated list of chromosomes')
    
#     args = parser.parse_args()
    
#     # Validate inputs
#     if not os.path.isdir(args.code_repo):
#         sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
#     # Create reference directory (ensure it's the main dir, not logs)
#     os.makedirs(args.ref_dir, exist_ok=True)
    
#     # Use absolute path to nextflow
#     nextflow_path = os.path.join(args.code_repo, 'nextflow')
#     if not os.path.exists(nextflow_path):
#         sys.exit(f"Error: Nextflow not found at {nextflow_path}")
    
#     # Set up environment
#     env = os.environ.copy()
#     env['PATH'] = f"{args.code_repo}:{env['PATH']}"
    
#     # Create log directory INSIDE reference directory
#     log_dir = os.path.join(args.ref_dir, "logs")
#     os.makedirs(log_dir, exist_ok=True)
    
#     print(f"Starting GWAS Harmonizer Setup")
#     print(f"Code repo: {args.code_repo}")
#     print(f"Reference dir: {args.ref_dir}")  # This should be the main directory
#     print(f"Log dir: {log_dir}")  # This is the subdirectory for logs
#     print(f"Chromosomes: {args.chromlist}")
#     print(f"Nextflow path: {nextflow_path}")
    
#     # Build Nextflow command - CRITICAL FIX: use args.ref_dir (main dir) not log_dir
#     cmd = [
#         nextflow_path, 'run', args.code_repo,
#         '-profile', 'standard',
#         '--reference',
#         '--ref', args.ref_dir,  # FIXED: Use main reference directory, not logs
#         '--chromlist', args.chromlist,
#         '-with-report', os.path.join(log_dir, 'ref-report.html'),
#         '-with-timeline', os.path.join(log_dir, 'ref-timeline.html'),
#         '-with-trace', os.path.join(log_dir, 'ref-trace.txt'),
#         '-with-dag', os.path.join(log_dir, 'ref-dag.html')
#     ]
    
#     print(f"Nextflow command: {' '.join(cmd)}")
    
#     # Run Nextflow
#     log_file = os.path.join(log_dir, 'ref.log')
#     try:
#         with open(log_file, 'w') as log_f:
#             log_f.write(f"Command: {' '.join(cmd)}\n")
#             log_f.write(f"Reference directory: {args.ref_dir}\n")
#             log_f.write(f"Log directory: {log_dir}\n")
#             log_f.flush()
            
#             process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
#             # Stream output with timestamps
#             import datetime
#             line_count = 0
#             for line in process.stdout:
#                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 output_line = f"[{timestamp}] {line}"
#                 print(output_line, end='')
#                 log_f.write(output_line)
#                 log_f.flush()
                
#                 line_count += 1
#                 if line_count % 50 == 0:
#                     print(f"=== Processed {line_count} lines of output ===")
            
#             return_code = process.wait()
            
#         if return_code != 0:
#             print(f"Nextflow process failed with return code: {return_code}")
#             sys.exit(return_code)
            
#         print("Harmonizer setup completed successfully!")
            
#         # Create output files for Galaxy
#         with open('log_dir.txt', 'w') as f:
#             f.write(log_dir)
            
#         # Copy report files to current directory for Galaxy outputs
#         report_files = {
#             'ref-report.html': 'report',
#             'ref-timeline.html': 'timeline'
#         }
        
#         for src_file, dest_name in report_files.items():
#             src = os.path.join(log_dir, src_file)
#             if os.path.exists(src):
#                 shutil.copy2(src, dest_name)
#                 print(f"Copied {src} to {dest_name}")
#             else:
#                 print(f"Warning: {src} not found")
                
#     except Exception as e:
#         sys.exit(f"Error running harmonizer setup: {str(e)}")

# if __name__ == '__main__':
#     main()















#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil
import signal
import time
from pathlib import Path

def run_command(cmd, env=None, timeout=7200):
    """Run command with timeout and real-time output"""
    print(f"Executing: {' '.join(cmd)}")
    sys.stdout.flush()
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        output_lines = []
        start_time = time.time()
        
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"ERROR: Process timed out after {timeout} seconds")
                process.terminate()
                return 1
                
            # Check if process is done
            if process.poll() is not None:
                break
                
            # Read line
            line = process.stdout.readline()
            if line:
                print(line, end='')
                output_lines.append(line)
                sys.stdout.flush()
            
            time.sleep(0.1)
        
        # Get any remaining output
        remaining, _ = process.communicate()
        if remaining:
            print(remaining, end='')
            output_lines.append(remaining)
        
        return process.returncode
        
    except Exception as e:
        print(f"ERROR: Failed to execute command: {str(e)}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='GWAS Harmonizer Setup Wrapper')
    parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory')
    parser.add_argument('--chromlist', required=True, help='Comma-separated list of chromosomes')
    
    args = parser.parse_args()
    
    print(f"GWAS Harmonizer Setup Started")
    print(f"Code repository: {args.code_repo}")
    print(f"Reference directory: {args.ref_dir}")
    print(f"Chromosomes: {args.chromlist}")
    
    # Validate inputs
    if not os.path.isdir(args.code_repo):
        sys.exit(f"ERROR: Code repository not found: {args.code_repo}")
    
    nextflow_path = os.path.join(args.code_repo, 'nextflow')
    if not os.path.isfile(nextflow_path):
        sys.exit(f"ERROR: Nextflow not found at: {nextflow_path}")
    
    # Create directories
    os.makedirs(args.ref_dir, exist_ok=True)
    log_dir = os.path.join(args.ref_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up environment
    env = os.environ.copy()
    env['PATH'] = f"{args.code_repo}:{env['PATH']}"
    
    # Build Nextflow command
    cmd = [
        nextflow_path, 'run', args.code_repo,
        '-profile', 'standard',
        '--reference',
        '--ref', args.ref_dir,
        '--chromlist', args.chromlist,
        '-with-report', os.path.join(log_dir, 'ref-report.html'),
        '-with-timeline', os.path.join(log_dir, 'ref-timeline.html'),
        '-with-trace', os.path.join(log_dir, 'ref-trace.txt'),
        '-with-dag', os.path.join(log_dir, 'ref-dag.html')
    ]
    
    # Run Nextflow
    return_code = run_command(cmd, env=env, timeout=7200)
    
    if return_code != 0:
        sys.exit(f"ERROR: Nextflow failed with exit code {return_code}")
    
    print("SUCCESS: GWAS Harmonizer setup completed!")
    
    # Create Galaxy outputs
    with open('log_dir.txt', 'w') as f:
        f.write(log_dir)
    
    # Copy report files
    report_src = os.path.join(log_dir, 'ref-report.html')
    timeline_src = os.path.join(log_dir, 'ref-timeline.html')
    
    if os.path.exists(report_src):
        shutil.copy2(report_src, 'report.html')
        print(f"Copied report to report.html")
    else:
        print("WARNING: Report file not found")
        open('report.html', 'w').close()  # Create empty file
    
    if os.path.exists(timeline_src):
        shutil.copy2(timeline_src, 'timeline.html')
        print(f"Copied timeline to timeline.html")
    else:
        print("WARNING: Timeline file not found")
        open('timeline.html', 'w').close()  # Create empty file

if __name__ == '__main__':
    main()