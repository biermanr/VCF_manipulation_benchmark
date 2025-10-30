#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "cyvcf2",
# ]
# ///

from cyvcf2 import VCF, Writer
import argparse

parser = argparse.ArgumentParser(description='Modify VCF IDs using cyvcf2')
parser.add_argument('-i', '--input', required=True, help='Input VCF file')
parser.add_argument('-o', '--output', required=True, help='Output VCF file')
args = parser.parse_args()

vcf = VCF(args.input)
w = Writer(args.output, vcf)

for v in vcf:
    v.ID = f"{v.CHROM}:{v.POS}:{v.REF}:{v.ALT[0]}"
    w.write_record(v)

w.close()
vcf.close()
