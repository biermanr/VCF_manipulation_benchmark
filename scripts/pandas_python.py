#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pandas",
# ]
# ///
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Modify VCF IDs using pandas")
parser.add_argument("-i", "--input", required=True, help="Input VCF file")
parser.add_argument("-o", "--output", required=True, help="Output VCF file")
args = parser.parse_args()

out_f = open(args.output, "w")

# Wirte header lines directly to output
with open(args.input) as in_f:
    for line in in_f:
        if not line.startswith("#"):
            break

        out_f.write(line)

# Read VCF data (skip header lines)
df = pd.read_csv(
    args.input,
    sep="\t",
    comment="#",
    header=None
)

# Update ID column (column index 2) to match new coordinates
df[2] = df[0].astype(str) + ":" + df[1].astype(str) + ":" + df[3] + ":" + df[4]

# Append data to VCF output
df.to_csv(out_f, sep="\t", index=False, header=False, mode="a")

out_f.close()
