# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "scikit-allel",
# ]
# ///

# NOTE
# scikit-allel `write_vcf` doesn't output genotypes and
# also changes which headers are written out so the output
# VCF isn't going to match the other approaches.

import allel
import argparse

parser = argparse.ArgumentParser(description='Modify VCF IDs using vanilla python')
parser.add_argument('-i', '--input', required=True, help='Input VCF file')
parser.add_argument('-o', '--output', required=True, help='Output VCF file')
args = parser.parse_args()

# Read VCF using scikit-allel
callset = allel.read_vcf(args.input)

# Update IDs directly in callset
callset['variants/ID'] = [f"{chrom}:{pos}:{ref}:{alt}"
                           for chrom, pos, ref, alt in zip(
                               callset['variants/CHROM'],
                               callset['variants/POS'],
                               callset['variants/REF'],
                               callset['variants/ALT'][:, 0]
                           )]

# Write output with updated IDs using write_vcf
allel.write_vcf(args.output, callset)
