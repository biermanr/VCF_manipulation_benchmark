#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse

parser = argparse.ArgumentParser(description='Modify VCF IDs using vanilla python')
parser.add_argument('-i', '--input', required=True, help='Input VCF file')
parser.add_argument('-o', '--output', required=True, help='Output VCF file')
args = parser.parse_args()

with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        # Output header lines unchanged 
        if line.startswith("#"):
            f_out.write(line)
            continue

        # Change ID column (2nd) and write out 
        m = line.split("\t")
        m[2] = m[0]+":"+m[1]+":"+m[3]+":"+m[4]
        line = "\t".join(m)
        f_out.write(line)

