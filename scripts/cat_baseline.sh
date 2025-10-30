#!/usr/bin/env bash
set -euo pipefail

# Function to display usage
usage() {
    echo "Usage: $0 -i <input_vcf> -o <output_vcf>"
    echo "  -i    Input VCF file"
    echo "  -o    Output VCF file"
    exit 1
}

# Initialize variables
VCF_IN=""
VCF_OUT=""

# Parse command line arguments
while getopts "i:o:h" opt; do
    case $opt in
        i)
            VCF_IN="$OPTARG"
            ;;
        o)
            VCF_OUT="$OPTARG"
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "$VCF_IN" ] || [ -z "$VCF_OUT" ]; then
    echo "Error: Both input and output VCF files must be specified." >&2
    usage
fi

# Run cat command
cat "$VCF_IN" > "$VCF_OUT"
