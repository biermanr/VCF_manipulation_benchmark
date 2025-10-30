
I had a simple text editing problem task where I had a 
tabular file with multiple rows of headers and I needed to create
a new file that was identical except for one of the columns.

I decided it would be fun to take some time and try a few different
approaches and see which ones I liked best. This repo is a way for
me to keep track of my thoughts and share for anyone who is interested
in different approaches to a simple problem.

For anyone curious, and it doesn't matter much for this problem, I was
working with a Variant Call Format (VCF) file which is a standard format
for some bioinformatics datasets. This VCF was the result of lifting 
over a previous VCF from an old to more modern reference genome.

Here's part of what the file looked like and the most important features
to notice is that there are potentially a LOT of ## metadata lines before
a # header line followed by tab-separated columns of genetic info. The
rows are longer than is shown here, but we only really care about the
`ID` column.

```
...
##contig=<ID=Un_MU018865v1,length=63180,assemb
##contig=<ID=X,length=124992030,assembly=UU_Cf
##contig=<ID=Y_NC_051844.1,length=3937623,asse
##contig=<ID=Y_unplaced_NW_024010443.1,length=
##contig=<ID=Y_unplaced_NW_024010444.1,length=
##liftOverProgram=CrossMap,version=0.6.4,websi
##liftOverChainFile=canFam3.canFam4.all.chain.
##originalFile=canFam3_AncestryReferencePanel.
##targetRefGenome=/scratch/gpfs/AKEY/DAP_bams_
##liftOverDate=October01,2025
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO  
1	447883	1:479620:G:A	G	A	.	.	PR
1	607787	1:639707:T:A	T	A	.	.	PR
1	692572	1:725068:T:C	T	C	.	.	PR
1	758613	1:788741:C:T	C	T	.	.	PR
1	857484	1:888003:G:A	G	A	.	.	PR
1	1195975	1:1224341:C:A	C	A	.	.	PR
1	1470610	1:1498884:G:A	G	A	.	.	PR
1	1723479	1:1752066:G:A	G	A	.	.	PR
```

The issue is that the `ID` column need to match the `POS` column.
For example the first data row has `ID` as `1:479620:G:A` but the `POS`
for that row is `447883` so we need to change the `ID` to be `1:447883:G:A`

Thankfully this is easy to fix with awk by running:

```
# Update SNP IDs to match new coordinates
awk -v OFS='\t' '$1 !~ "^#" { $3="chr"$1":"$2":"$4":"$5 } 1' $VCF_IN > $VCF_OUT
```

where `$VCF_IN` is the path to the incorrect input VCF, and `$VCF_OUT` is the
new corrected file. I probably don't even need to have `$1 !~ "^#"` which is
there to skip changing the `ID` column for the metadata and header rows.

I was fairly happy with this approach, but then I became curious if it was any
faster than a "vanilla" python approach which reads the input VCF line by line.
Or how this AWK approach would compare to using pandas or VCF'specific libraries.
Or even how it compares to the same script written in rust.

For the comparisons of these approaches I decided I'd just wget a VCF from online
in a github action rather than uploading the actual VCF that sparked this question.

```
wget -q -O - https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/1kGP_high_coverage_Illumina.chr22.filtered.SNV_INDEL_SV_phased_panel.vcf.gz | gunzip -c | head -n 100000 > example.vcf
```

This VCF is already correct, the `ID` column doesn't need fixing, but I'm just going to pretend that it
does and run all the necessary steps to "fix" it so that I can benchmark the different approaches. This
VCF is 14G unzipped. Some of the approaches can work directly with gzipped files, but I'm deciding to
start with an unzipped file for all approaches and not count that against their time/memory usage.
I'm only downloading the first 100,000 lines of this VCF as a test dataset that's ~1.3G in size and
I'm replacing the `ID` column with `.` so the scripts make more obvious changes.

Here are part of the first few data rows including some metadata lines and the header:
```
##INFO=<ID=END2,Type=Integer,Number=1,Descriptio
##INFO=<ID=ALGORITHMS,Number=.,Type=String,Descr
##INFO=<ID=SOURCE,Number=1,Type=String,Descripti
##INFO=<ID=EVIDENCE,Number=.,Type=String,Descrip
##INFO=<ID=END,Number=1,Type=Integer,Description
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	
chr22	10519265	.	CA	C	
chr22	10519276	.	G	C	.	
chr22	10519389	.	T	C	.	
chr22	10519410	.	G	A	.	
chr22	10519412	.	G	T	.	
```

All the scripts are going to replace the `ID` column with the
information in the surrounding columns `{#CHROM}:{POS}:{REF}:{ALT}`
so that the output.vcf in this example is:
```
##INFO=<ID=END2,Type=Integer,Number=1,Descriptio
##INFO=<ID=ALGORITHMS,Number=.,Type=String,Descr
##INFO=<ID=SOURCE,Number=1,Type=String,Descripti
##INFO=<ID=EVIDENCE,Number=.,Type=String,Descrip
##INFO=<ID=END,Number=1,Type=Integer,Description
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	
chr22	10519265	chr22:10519265:CA:C	CA	C	
chr22	10519276	chr22:10519276:G:C	G	C	.	
chr22	10519389	chr22:10519389:T:C	T	C	.	
chr22	10519410	chr22:10519410:G:A	G	A	.	
chr22	10519412	chr22:10519412:G:T	G	T	.	
```





I've created a script `scripts/awk_approach.sbatch` which runs this command, and this is successful.


I've created additional scripts such as `scripts/run_vanilla_python.sbatch` and corresponding `scripts/vanilla_python.py`
which produces the exact same output as the awk approach for comparison.

I had trouble getting `scikit-allel` to work with `write_vcf` so I gave up on it since it's marked as "Preliminary"
in the documentation. I think this is surprising. The output is wrong/truncated but I'll still benchmark it.

It was also suggested to me to try cyvcf2 which I've never used before.
This was really nice to write and reads like english. It's just a bit slower than
some of the other approaches. I'm guessing this is because it's fully parsing
the VCF including the genotypes, while the other approaches just parse the
first few columns. Would be interesting to do a comparison between the tools
for a more complex VCF task.




