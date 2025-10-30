# VCF ID Replacement Approaches

## Overview

This project explores and benchmarks different approaches to solving a simple text processing problem: updating the ID column in a VCF (Variant Call Format) file to match position information from other columns.

## The Problem

I had a VCF file where the ID column needed to be updated to match the genomic position. Specifically, the ID column needed to be replaced with a concatenation of: `{CHROM}:{POS}:{REF}:{ALT}`.

### Background

The VCF was the result of lifting over from an older reference genome (canFam3) to a more modern one (canFam4). After the liftover, the ID column still contained the old coordinates but the POS column had the new coordinates.

### Example

**Before:**
```
#CHROM  POS      ID              REF  ALT  ...
1       447883   1:479620:G:A    G    A    ...
```

**After:**
```
#CHROM  POS      ID              REF  ALT  ...
1       447883   1:447883:G:A    G    A    ...
```

## Motivation

While I initially solved this with AWK, I became curious about:

- How does AWK performance compare to vanilla Python?
- What about specialized libraries like pandas, cyvcf2, or scikit-allel?
- How would a compiled language like Rust perform?
- What are the trade-offs in terms of code readability vs performance?

## Test Dataset

For benchmarking, we use a real-world VCF from the 1000 Genomes Project:

- Source: [1000G High Coverage Illumina chr22 VCF](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/)
- Size: First 100,000 lines (~1.3GB)
- Modified: ID column replaced with `.` to simulate the problem

### Test File Structure

```
##INFO=<ID=END2,Type=Integer,Number=1,Description=...>
##INFO=<ID=ALGORITHMS,Number=.,Type=String,Description=...>
...
#CHROM  POS       ID  REF  ALT  QUAL  FILTER  INFO
chr22   10519265  .   CA   C    .     .       ...
chr22   10519276  .   G    C    .     .       ...
chr22   10519389  .   T    C    .     .       ...
```

## Approaches Tested

We test 9 different approaches:

1. **Baseline (cat)**: Simple file copy to measure I/O overhead
2. **AWK**: Classic Unix text processing tool
3. **Python (vanilla)**: Basic Python with string split/join
4. **Python (maxsplit)**: Optimized split with maxsplit parameter
5. **Python (maxsplit + dowhile)**: Further optimized header handling
6. **Python (pandas)**: Using the pandas DataFrame library
7. **Python (cyvcf2)**: VCF-specific library with htslib bindings
8. **Python (scikit-allel)**: Genomics-focused library
9. **Rust**: Compiled systems programming language

## Evaluation Metrics

For each approach, we measure:

- **Execution Time** (seconds): Wall-clock time to process the file
- **Peak Memory Usage** (KB): Maximum resident set size
- **MD5 Checksum**: Verify output correctness

## Findings

See the [Results](results.md) page for detailed benchmark data and the [Conclusions](conclusions.md) page for analysis and lessons learned.
