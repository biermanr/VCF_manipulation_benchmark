#!/usr/bin/env -S uv run --script
"""
Generate results documentation from benchmark JSON files.
This script reads all the benchmark results and generates a markdown file
with tables and mermaid.js charts for visualization.
"""

import json
import os
from pathlib import Path
from typing import List, Dict

def load_results(results_dir: Path) -> List[Dict]:
    """Load all result JSON files from the results directory."""
    results = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file == 'results.json':
                filepath = Path(root) / file
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    results.append(data)

    # Sort by time for consistent ordering
    results.sort(key=lambda x: float(x['time_seconds']))

    return results

def format_approach_name(approach: str) -> str:
    """Convert approach ID to human-readable name."""
    name_map = {
        'baseline_cat': 'Baseline (cat)',
        'awk': 'AWK',
        'python_vanilla': 'Python (vanilla)',
        'python_maxsplit': 'Python (maxsplit)',
        'python_maxsplit_dowhile': 'Python (maxsplit+dowhile)',
        'python_pandas': 'Python (pandas)',
        'python_cyvcf2': 'Python (cyvcf2)',
        'python_scikit_allel': 'Python (scikit-allel)',
        'rust': 'Rust',
    }
    return name_map.get(approach, approach)

def generate_time_chart(results: List[Dict]) -> str:
    """Generate mermaid.js xychart for execution time."""

    # Prepare data
    labels = [format_approach_name(r['approach']) for r in results]
    times = [float(r['time_seconds']) for r in results]

    # Build mermaid chart - split header and body to avoid format string issues with {init}
    chart_header = """```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Execution Time by Approach"
"""
    chart_body = """    x-axis [{}]
    y-axis "Time (seconds)" 0 --> {}
    bar [{}]
```""".format(
        ', '.join(f'"{label}"' for label in labels),
        max(times) * 1.1,  # Add 10% headroom
        ', '.join(str(t) for t in times)
    )

    return chart_header + chart_body

def generate_memory_chart(results: List[Dict]) -> str:
    """Generate mermaid.js xychart for memory usage."""

    # Sort by memory for this chart
    sorted_results = sorted(results, key=lambda x: float(x['memory_kb']))

    labels = [format_approach_name(r['approach']) for r in sorted_results]
    memory_mb = [float(r['memory_kb']) / 1024 for r in sorted_results]

    # Build mermaid chart - split header and body to avoid format string issues with {init}
    chart_header = """```mermaid
%%{init: {'theme':'base'}}%%
xychart-beta
    title "Peak Memory Usage by Approach"
"""
    chart_body = """    x-axis [{}]
    y-axis "Memory (MB)" 0 --> {}
    bar [{}]
```""".format(
        ', '.join(f'"{label}"' for label in labels),
        max(memory_mb) * 1.1,  # Add 10% headroom
        ', '.join(f'{m:.1f}' for m in memory_mb)
    )

    return chart_header + chart_body

def generate_results_table(results: List[Dict]) -> str:
    """Generate markdown table with all results."""

    table = """| Approach | Time (seconds) | Memory (MB) | MD5 Checksum | Notes |
|----------|---------------|-------------|--------------|-------|
"""

    # Find the most common MD5 (should be the correct one)
    md5_counts = {}
    for r in results:
        md5 = r.get('md5', 'N/A')
        md5_counts[md5] = md5_counts.get(md5, 0) + 1

    expected_md5 = max(md5_counts.items(), key=lambda x: x[1])[0] if md5_counts else None

    for r in results:
        approach = format_approach_name(r['approach'])
        time_sec = float(r['time_seconds'])
        memory_mb = float(r['memory_kb']) / 1024
        md5 = r.get('md5', 'N/A')
        note = r.get('note', '')

        # Add checkmark or warning for MD5
        md5_display = md5[:8] + '...'
        if md5 != expected_md5 and expected_md5:
            md5_display += ' ⚠️'
        else:
            md5_display += ' ✓'

        table += f"| {approach} | {time_sec:.3f} | {memory_mb:.1f} | `{md5_display}` | {note} |\n"

    return table

def generate_md5_section(results: List[Dict]) -> str:
    """Generate detailed MD5 checksum section."""

    section = """## MD5 Checksums

The following table shows the MD5 checksums of the output files. All approaches should produce identical output (except scikit-allel, which has known limitations).

| Approach | MD5 Checksum |
|----------|--------------|
"""

    for r in results:
        approach = format_approach_name(r['approach'])
        md5 = r.get('md5', 'N/A')
        section += f"| {approach} | `{md5}` |\n"

    # Add validation note
    md5_values = [r.get('md5', 'N/A') for r in results if r['approach'] != 'baseline_cat' and r['approach'] != 'python_scikit_allel']
    unique_md5s = set(md5_values)

    if len(unique_md5s) == 1:
        section += "\n!!! success \"Validation Passed\"\n"
        section += "    All approaches (except baseline and scikit-allel) produce identical output files. ✓\n"
    else:
        section += "\n!!! warning \"MD5 Mismatch\"\n"
        section += f"    Found {len(unique_md5s)} different MD5 checksums. Some approaches may be producing different output.\n"

    return section

def generate_performance_insights(results: List[Dict]) -> str:
    """Generate insights section comparing performance."""

    # Exclude baseline for comparisons
    processing_results = [r for r in results if r['approach'] != 'baseline_cat']

    if not processing_results:
        return ""

    fastest = min(processing_results, key=lambda x: float(x['time_seconds']))
    slowest = max(processing_results, key=lambda x: float(x['time_seconds']))
    least_memory = min(processing_results, key=lambda x: float(x['memory_kb']))
    most_memory = max(processing_results, key=lambda x: float(x['memory_kb']))

    baseline = next((r for r in results if r['approach'] == 'baseline_cat'), None)

    section = """## Performance Insights

### Speed
"""

    section += f"- **Fastest**: {format_approach_name(fastest['approach'])} at {float(fastest['time_seconds']):.3f} seconds\n"
    section += f"- **Slowest**: {format_approach_name(slowest['approach'])} at {float(slowest['time_seconds']):.3f} seconds\n"

    speedup = float(slowest['time_seconds']) / float(fastest['time_seconds'])
    section += f"- **Speed difference**: {speedup:.2f}x (fastest vs slowest)\n"

    if baseline:
        overhead = float(fastest['time_seconds']) - float(baseline['time_seconds'])
        overhead_pct = (overhead / float(baseline['time_seconds'])) * 100
        section += f"- **Minimum processing overhead**: {overhead:.3f} seconds ({overhead_pct:.1f}% over baseline I/O)\n"

    section += "\n### Memory\n\n"
    section += f"- **Least memory**: {format_approach_name(least_memory['approach'])} at {float(least_memory['memory_kb'])/1024:.1f} MB\n"
    section += f"- **Most memory**: {format_approach_name(most_memory['approach'])} at {float(most_memory['memory_kb'])/1024:.1f} MB\n"

    mem_ratio = float(most_memory['memory_kb']) / float(least_memory['memory_kb'])
    section += f"- **Memory difference**: {mem_ratio:.2f}x (most vs least)\n"

    return section

def main():
    """Main function to generate results documentation."""

    # Paths
    results_dir = Path('results')
    output_file = Path('docs/results.md')

    print(f"Loading results from {results_dir}...")
    results = load_results(results_dir)

    print(f"Found {len(results)} result files")

    if not results:
        print("No results found! Generating placeholder.")
        with open(output_file, 'w') as f:
            f.write("# Benchmark Results\n\n")
            f.write("!!! warning \"No Results\"\n")
            f.write("    No benchmark results were found. The workflow may have failed.\n")
        return

    # Generate content sections
    print("Generating charts and tables...")
    time_chart = generate_time_chart(results)
    memory_chart = generate_memory_chart(results)
    results_table = generate_results_table(results)
    md5_section = generate_md5_section(results)
    insights = generate_performance_insights(results)

    # Build full markdown document
    content = f"""# Benchmark Results

!!! info "Auto-Generated Results"
    This page is automatically generated by the GitHub Actions workflow. Results are updated with each run.

## Performance Overview

The charts and tables below show the performance characteristics of each approach when processing a 1.3GB VCF file with 100,000 lines.

{insights}

## Execution Time Comparison

{time_chart}

## Memory Usage Comparison

{memory_chart}

## Detailed Results

{results_table}

{md5_section}

## Interpreting the Results

### Time (seconds)
- Lower is better
- Includes reading input, processing, and writing output
- Baseline (cat) shows the minimum time for pure I/O

### Memory (MB)
- Lower is better for most use cases
- Peak resident set size (RSS) during execution
- High memory approaches may struggle with very large files

### MD5 Checksums
- All approaches should produce identical output (except scikit-allel)
- Mismatches indicate bugs or different behavior
- Baseline (cat) has a different checksum since it doesn't modify the file

## Notes

- All benchmarks run on GitHub Actions ubuntu-latest runners
- Results may vary slightly between runs due to system load
- Times measured with `/usr/bin/time -f "%e %M"`
- See [Approaches](approaches.md) for implementation details
"""

    # Write to file
    print(f"Writing results to {output_file}...")
    with open(output_file, 'w') as f:
        f.write(content)

    print("✓ Results documentation generated successfully!")

    # Print summary to console
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    for r in results:
        print(f"{format_approach_name(r['approach']):30} {float(r['time_seconds']):6.3f}s  {float(r['memory_kb'])/1024:6.1f}MB")
    print("="*60)

if __name__ == '__main__':
    main()
