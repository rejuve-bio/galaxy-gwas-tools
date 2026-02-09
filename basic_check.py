import sys
import gwaslab as gl

try:
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print("=== GWASLab Basic Check ===")

    sumstats = gl.Sumstats(input_file, fmt="plink2")

    # Run basic checks
    check_report = sumstats.basic_check()

    # Save check results
    print(check_report)

except Exception as e:
    with open(output_file, "w") as f:
        f.write(f"Error: {e}")
