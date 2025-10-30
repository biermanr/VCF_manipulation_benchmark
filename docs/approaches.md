# Approaches

This page describes each approach in detail, including code examples and implementation notes.

## 1. Baseline (cat)

**Purpose**: Establish a lower bound for I/O performance.

Simply copies the file without making any modifications:

```bash
cat example.vcf > cat_out.vcf
```

This measures the unavoidable cost of reading and writing the file.

---

## 2. AWK

**Language**: Shell/AWK
**File**: `scripts/awk_approach.sh`

Classic Unix approach using AWK for text processing:

```bash
awk -v OFS='\t' '$1 !~ "^#" { $3=$1":"$2":"$4":"$5 } 1' input.vcf > output.vcf
```

**How it works**:

- `$1 !~ "^#"`: Skip header lines starting with `#`
- `$3=$1":"$2":"$4":"$5`: Replace ID column (field 3) with concatenated values
- `1`: Print every line (modified or not)
- `-v OFS='\t'`: Set output field separator to tab

**Pros**:

- Concise, single-line solution
- Fast for line-by-line processing
- No dependencies beyond standard Unix tools

**Cons**:

- Syntax can be cryptic for those unfamiliar with AWK
- Limited error handling

---

## 3. Python (Vanilla)

**Language**: Python 3.12
**File**: `scripts/vanilla_python.py`
**Dependencies**: None

Basic Python implementation using string operations:

```python
with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        if line.startswith("#"):
            f_out.write(line)
            continue

        m = line.split("\t")
        m[2] = "chr"+m[0]+":"+m[1]+":"+m[3]+":"+m[4]
        line = "\t".join(m)
        f_out.write(line)
```

**How it works**:

- Read file line by line
- Skip header lines unchanged
- Split each data line on tabs
- Replace ID column (index 2)
- Rejoin and write

**Pros**:

- Easy to read and understand
- No external dependencies
- Good starting point for Python developers

**Cons**:

- Splits all columns even though we only need the first 5
- Rejoins entire line unnecessarily

---

## 4. Python (Maxsplit)

**Language**: Python 3.12
**File**: `scripts/vanilla_maxsplit_python.py`
**Dependencies**: None

Optimized version using `maxsplit` parameter:

```python
with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        if line.startswith("#"):
            f_out.write(line)
            continue

        chrom, pos, _, ref, alt, rest = line.split("\t", maxsplit=5)
        f_out.write(f"{chrom}\t{pos}\t{chrom}:{pos}:{ref}:{alt}\t{ref}\t{alt}\t{rest}")
```

**How it works**:

- Use `maxsplit=5` to only split the first 6 fields
- Keeps the rest of the line as a single string
- Avoids unnecessary string concatenation

**Pros**:

- More efficient than vanilla approach
- Still readable and simple
- Avoids processing columns we don't need

**Cons**:

- Still checks for headers on every line

---

## 5. Python (Maxsplit + DoWhile)

**Language**: Python 3.12
**File**: `scripts/vanilla_maxsplit_dowhile_python.py`
**Dependencies**: None

Further optimized with separate header handling:

```python
with open(args.input) as f_in, open(args.output, "w") as f_out:
    # Process all header lines first
    for line in f_in:
        if not line.startswith("#"):
            break
        f_out.write(line)

    # Process remaining data lines
    while line:
        chrom, pos, _, ref, alt, rest = line.split("\t", maxsplit=5)
        f_out.write(f"{chrom}\t{pos}\t{chrom}:{pos}:{ref}:{alt}\t{ref}\t{alt}\t{rest}")
        line = f_in.readline()
```

**How it works**:

- First loop processes all headers until first data line
- Second loop processes data lines without checking for `#`
- Avoids redundant header checks for every data line

**Pros**:

- Most optimized vanilla Python approach
- Eliminates unnecessary conditionals
- Still pure Python with no dependencies

**Cons**:

- Slightly more complex control flow
- Uses `readline()` instead of iterator

---

## 6. Python (pandas)

**Language**: Python 3.12
**File**: `scripts/pandas_python.py`
**Dependencies**: pandas

Uses pandas DataFrame for processing:

```python
# Write headers manually
with open(args.input) as in_f:
    for line in in_f:
        if not line.startswith("#"):
            break
        out_f.write(line)

# Read data with pandas
df = pd.read_csv(args.input, sep="\t", comment="#", header=None)

# Update ID column
df[2] = df[0].astype(str) + ":" + df[1].astype(str) + ":" + df[3] + ":" + df[4]

# Write output
df.to_csv(out_f, sep="\t", index=False, header=False, mode="a")
```

**How it works**:

- Manually writes headers first
- Loads all data into memory as DataFrame
- Vectorized string operations to create new ID column
- Writes entire DataFrame to output

**Pros**:

- Familiar to data scientists
- Vectorized operations can be fast
- Good for more complex transformations

**Cons**:

- Loads entire file into memory
- Heavy dependency for simple task
- Type conversions add overhead

---

## 7. Python (cyvcf2)

**Language**: Python 3.12
**File**: `scripts/cyvcf2_python.py`
**Dependencies**: cyvcf2

VCF-specific library with htslib bindings:

```python
vcf = VCF(args.input)
w = Writer(args.output, vcf)

for v in vcf:
    v.ID = f"{v.CHROM}:{v.POS}:{v.REF}:{v.ALT[0]}"
    w.write_record(v)

w.close()
vcf.close()
```

**How it works**:

- Uses C library (htslib) for VCF parsing
- Provides object-oriented interface to VCF records
- Fully parses and validates VCF structure

**Pros**:

- Very readable and Pythonic
- Properly handles VCF format complexities
- Useful for more complex VCF operations

**Cons**:

- Fully parses all fields including genotypes (overkill for this task)
- Slower than simpler approaches for basic text processing

---

## 8. Python (scikit-allel)

**Language**: Python 3.12
**File**: `scripts/scikit_allel_python.py`
**Dependencies**: scikit-allel

Genomics-focused library:

```python
callset = allel.read_vcf(args.input)

callset['variants/ID'] = [
    f"{chrom}:{pos}:{ref}:{alt}"
    for chrom, pos, ref, alt in zip(
        callset['variants/CHROM'],
        callset['variants/POS'],
        callset['variants/REF'],
        callset['variants/ALT'][:, 0]
    )
]

allel.write_vcf(args.output, callset)
```

**How it works**:

- Loads entire VCF into memory as numpy arrays
- Updates ID array
- Writes back to VCF

**Pros**:

- Designed for population genetics analyses
- Numpy array backend for complex operations

**Cons**:

- `write_vcf` is marked as "Preliminary" in docs
- **Does NOT output genotypes** - incomplete VCF output
- Loads entire file into memory
- Not suitable for this simple task

!!! warning "Output Limitations"
    The scikit-allel approach produces different output than other methods because `write_vcf` does not output genotype data. MD5 checksums will differ.

---

## 9. Rust

**Language**: Rust
**File**: `scripts/rust_approach.rs`
**Dependencies**: None (std library only)

Compiled systems programming approach:

```rust
let input = File::open(vcf_in)?;
let reader = BufReader::new(input);
let output = File::create(vcf_out)?;
let mut writer = BufWriter::new(output);

for line in reader.lines() {
    let line = line?;

    if line.starts_with('#') {
        writeln!(writer, "{}", line)?;
        continue;
    }

    let mut splitter = line.splitn(6, '\t');
    let chrom = splitter.next().unwrap();
    let pos = splitter.next().unwrap();
    splitter.next(); // skip old id
    let ref_allele = splitter.next().unwrap();
    let alt_allele = splitter.next().unwrap();
    let remainder = splitter.next().unwrap();

    let id = format!("{chrom}:{pos}:{ref_allele}:{alt_allele}");
    let out_line = format!("{chrom}\t{pos}\t{id}\t{ref_allele}\t{alt_allele}\t{remainder}\n");

    writer.write_all(out_line.as_bytes())?;
}
```

**How it works**:

- Buffered I/O for efficient reading/writing
- Line-by-line processing with split iterator
- Compiled to native code with optimizations

**Pros**:

- Compiled language with potential for high performance
- Memory safe with zero-cost abstractions
- No runtime overhead

**Cons**:

- More verbose than scripting languages
- Requires compilation step
- Surprisingly slower in initial tests (may need optimization)

!!! note "Performance Note"
    The Rust implementation is currently slower than expected. This likely indicates room for optimization in the implementation rather than a limitation of the language itself.

---

## Summary

Each approach represents different trade-offs between:

- **Simplicity** vs **Performance**
- **Dependencies** vs **Capabilities**
- **Readability** vs **Efficiency**

See the [Results](results.md) page for quantitative performance comparisons.
