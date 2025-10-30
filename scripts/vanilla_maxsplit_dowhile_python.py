#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
import argparse

parser = argparse.ArgumentParser(description='Modify VCF IDs using vanilla python with maxsplit and do-while approach for headers')
parser.add_argument('-i', '--input', required=True, help='Input VCF file')
parser.add_argument('-o', '--output', required=True, help='Output VCF file')
args = parser.parse_args()

with open(args.input) as f_in, open(args.output, "w") as f_out:

    # Output header lines unchanged 
    for line in f_in:
        if not line.startswith("#"):
            break

        f_out.write(line)

    # The rest of the lines won't be headers. Adjust ID col and write
    while line:
        chrom,pos,_,ref,alt,rest = line.split("\t", maxsplit=5)
        f_out.write(f"{chrom}\t{pos}\t{chrom}:{pos}:{ref}:{alt}\t{ref}\t{alt}\t{rest}")

        line = f_in.readline()
