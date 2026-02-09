# import gwaslab as gl

# print("=== GWASLab Sumstats ===")
# try:
#     sumstats = gl.Sumstats("1kgeas.B1.glm.firth.gz", fmt="plink2")
#     print(sumstats)
# except Exception as e:
#     print(f"Failed to load sumstats: {e}")



# import sys
# import gwaslab as gl

# print("=== GWASLab Sumstats ===")

# try:
#     input_file = sys.argv[1]
#     sumstats = gl.Sumstats(input_file, fmt="plink2")
#     print(sumstats.data.head())
# except Exception as e:
#     print(f"Failed to load sumstats: {e}")



import sys
import gwaslab as gl

print("=== GWASLab Sumstats ===")

try:
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    sumstats = gl.Sumstats(input_file, fmt="plink2")
    
    # Save the dataframe to TSV
    sumstats.data.to_csv(output_file, sep="\t", index=False)

except Exception as e:
    print(f"Failed to load sumstats: {e}")
