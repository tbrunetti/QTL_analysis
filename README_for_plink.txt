# convert lgen format to plink binary (.fam, .map, and .lgen required in same space)
~/Downloads/software/plink --lfile test_prefix --make-bed --out test_prefix

# ensure only autosomes are in the data
~/Downloads/software/plink --bfile test_prefix --chr 1-19 --make-bed --out test_prefix_autosomes

# check missingness of snps and overall sample genotypes (note does not remove anything, just gets summary)
~/Downloads/software/plink --bfile test_prefix_autosomes --missing --out test_prefix_autosomes (output .imiss for sample genotyping missingness and .lmiss for snp missingness)
			
# Explore the summary data to see what you want to filter
ex: sort -k 5n,5 test_prefix_autosomes.lmiss | tail  will show you the top 10 snps with the highest missingness rates across all samples
you can then grep one of those snps in your final report to convince yourself:
grep "UNCJPD009349"  test_final_report.txt
and view snp info by grepping on the map
grep "UNCJPD009349" test_snp_map.txt

look at missingness in a sample overall
head test_prefix_autosomes.imiss 
see the highest 10 samples with the most missing calls:
sort -k6 -rn test_prefix_autosomes.imiss | head


# remove poor samples (if needed) and poor performing snps (--geno 0.05 means max missingness for a snp is 5%, --mind 0.05, means max missingness for a sample is 5%)
~/Downloads/software/plink --bfile test_prefix_autosomes --geno 0.05 --mind 0.05 --make-bed --out test_prefix_autosomes_snp_sample_filtered


# prune snps that carry redundant information
~/Downloads/software/plink --bfile test_prefix_autosomes_snp_sample_filtered --indep-pairwise 50kb 5 0.50 --out test_prefix_autosomes_snp_sample_filtered_ldpruned
~/Downloads/software/plink --bfile test_prefix_autosomes_snp_sample_filtered --exclude test_prefix_autosomes_snp_sample_filtered_ldpruned.prune.out --make-bed --out test_prefix_autosomes_snp_sample_filtered_ldpruned

# can look at polymorphic sites by calculating maf
~/Downloads/software/plink --bfile test_prefix_autosomes_snp_sample_filtered_ldpruned --freq --out test_prefix_autosomes_snp_sample_filtered_ldpruned
# 5th column is maf; maf with 0 mean site is monomorphic (i.e. snp is the same for all samples)
awk '{print $5}' test_prefix_autosomes_snp_sample_filtered_ldpruned.frq | sort | uniq -c

you can remove variants that provide little information based on monomorphic sites or low number of samples (if small sample size, be sure to pick something that is representative)
~/Downloads/software/plink --bfile test_prefix_autosomes_snp_sample_filtered_ldpruned --maf 0.05 --make-bed --out test_prefix_autosomes_snp_sample_ldpruned_maf_filtered
