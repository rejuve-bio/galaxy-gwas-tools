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

def run_nextflow_with_timeout(cmd, env, timeout=7200):  # 2 hour timeout
    """Run nextflow command with timeout handling"""
    try:
        # Start the process
        process = subprocess.Popen(
            cmd, 
            env=env,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            preexec_fn=os.setsid  # Create process group
        )
        
        # Read output in real-time with timeout
        start_time = time.time()
        output_lines = []
        
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"Process timed out after {timeout} seconds")
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                return 1
                
            # Check if process finished
            if process.poll() is not None:
                break
                
            # Read available output
            line = process.stdout.readline()
            if line:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                output_line = f"[{timestamp}] {line}"
                print(output_line, end='')
                output_lines.append(output_line)
                sys.stdout.flush()
            
            time.sleep(0.1)
        
        # Get any remaining output
        remaining_output, _ = process.communicate()
        if remaining_output:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {remaining_output}", end='')
            output_lines.append(f"[{timestamp}] {remaining_output}")
        
        return process.returncode
        
    except Exception as e:
        print(f"Error running nextflow: {str(e)}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='GWAS Harmonizer Setup Wrapper')
    parser.add_argument('--code-repo', required=True, help='Path to harmonizer code repository')
    parser.add_argument('--ref-dir', required=True, help='Reference data directory')
    parser.add_argument('--chromlist', default='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT',
                       help='Comma-separated list of chromosomes')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.isdir(args.code_repo):
        sys.exit(f"Error: Code repository not found: {args.code_repo}")
    
    # Create reference directory
    os.makedirs(args.ref_dir, exist_ok=True)
    
    # Use absolute path to nextflow
    nextflow_path = os.path.join(args.code_repo, 'nextflow')
    if not os.path.exists(nextflow_path):
        sys.exit(f"Error: Nextflow not found at {nextflow_path}")
    
    # Set up environment
    env = os.environ.copy()
    env['PATH'] = f"{args.code_repo}:{env['PATH']}"
    
    # Create log directory
    log_dir = os.path.join(args.ref_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    print(f"Starting GWAS Harmonizer Setup")
    print(f"Code repo: {args.code_repo}")
    print(f"Reference dir: {args.ref_dir}")
    print(f"Log dir: {log_dir}")
    print(f"Chromosomes: {args.chromlist}")
    print(f"Nextflow path: {nextflow_path}")
    
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
    
    print(f"Nextflow command: {' '.join(cmd)}")
    
    # Run Nextflow with proper process management
    log_file = os.path.join(log_dir, 'ref.log')
    try:
        with open(log_file, 'w') as log_f:
            log_f.write(f"Command: {' '.join(cmd)}\n")
            log_f.write(f"Reference directory: {args.ref_dir}\n")
            log_f.write(f"Log directory: {log_dir}\n")
            log_f.flush()
            
            return_code = run_nextflow_with_timeout(cmd, env, timeout=7200)  # 2 hour timeout
            
        if return_code != 0:
            print(f"Nextflow process failed with return code: {return_code}")
            sys.exit(return_code)
            
        print("Harmonizer setup completed successfully!")
            
        # Create output files for Galaxy
        with open('log_dir.txt', 'w') as f:
            f.write(log_dir)
            
        # Copy report files to current directory for Galaxy outputs
        report_files = {
            'ref-report.html': 'report',
            'ref-timeline.html': 'timeline'
        }
        
        for src_file, dest_name in report_files.items():
            src = os.path.join(log_dir, src_file)
            if os.path.exists(src):
                shutil.copy2(src, dest_name)
                print(f"Copied {src} to {dest_name}")
            else:
                print(f"Warning: {src} not found")
                
    except Exception as e:
        sys.exit(f"Error running harmonizer setup: {str(e)}")

if __name__ == '__main__':
    main()