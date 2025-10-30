#!/bin/bash
set -euo pipefail

URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/1kGP_high_coverage_Illumina.chr22.filtered.SNV_INDEL_SV_phased_panel.vcf.gz"

# Awk command is replacing the "ID" (3rd column) with "." for non-metadata/non-header rows
wget -q -O - $URL \
    | gunzip -c \
    | head -n 100000 \
    | awk -v OFS='\t' '$1 !~ "^#" { $3="." } 1' > example.vcf
