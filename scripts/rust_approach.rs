use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};

fn main() -> std::io::Result<()> {

    let args: Vec<String> = env::args().collect();

    let mut vcf_in: Option<String> = None;
    let mut vcf_out: Option<String> = None;

    // Should use clap instead
    for arg in args.iter().skip(1) { // Skip the program name
        match arg.as_str() {
            "-i" | "--input" => {
                // Assuming the next argument is the input file
                if let Some(index) = args.iter().position(|a| a == arg) {
                    if let Some(file) = args.get(index + 1) {
                        vcf_in = Some(file.clone());
                    }
                }
            }
            "-o" | "--output" => {
                // Assuming the next argument is the output file
                if let Some(index) = args.iter().position(|a| a == arg) {
                    if let Some(file) = args.get(index + 1) {
                        vcf_out = Some(file.clone());
                    }
                }
            }
            _ => {}
        }
    }

    let vcf_in = vcf_in.expect("Specify input VCF with --input");
    let vcf_out = vcf_out.expect("Specify input VCF with --input");

    // Read and process file

    let input = File::open(vcf_in)?;
    let reader = BufReader::new(input);

    let output = File::create(vcf_out)?;
    let mut writer = BufWriter::new(output);

    for line in reader.lines() {
        let line = line?;

        // TODO don't have to do this check after headers are passed
        // TODO maybe use take_until or something
        if line.starts_with('#') {
            writeln!(writer, "{}", line)?; //What's the diff between writeline and writer.write_all?
            continue;
        }

        // Parse the line
        let mut splitter = line.splitn(6, '\t');
        let chrom = splitter.next().unwrap();
        let pos = splitter.next().unwrap();
        splitter.next(); // old id, not used
        let ref_allele = splitter.next().unwrap();
        let alt_allele = splitter.next().unwrap();
        let remainder = splitter.next().unwrap();

        let id = format!("{chrom}:{pos}:{ref_allele}:{alt_allele}");
        let out_line = format!("{chrom}\t{pos}\t{id}\t{ref_allele}\t{alt_allele}\t{remainder}\n");

        writer.write_all(out_line.as_bytes())?;
    }

    writer.flush()?;
    Ok(())
}
