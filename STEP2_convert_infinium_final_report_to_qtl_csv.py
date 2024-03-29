awk -F"," '{print $1","$2","$3","$4","$5}' samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv

sed -i 's/SNP Name//' samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv
sed -i 's/chr//' samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv
sed -i 's/cM_cox//' samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv
sed -i 's/Sample ID,//' samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv

#sed -n '1p' testing_df1.csv 
#sed -n '2p' testing_df1.csv 
#sed -n '3p' testing_df1.csv 


head -n 1 samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv > main_header.txt
sed -n '2p;3p;' samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv > sub_header.txt #skip 4p b/c that is blank line

tail -n+5 samples_1_through_48_MURGIGV01_20180830_FinalReport_to_qtl_format.csv > body.txt
paste -d"," <(echo "Sample ID") main_header.txt  > final_main_header.txt

# next sample
sed -i 's/SNP Name//' samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv
sed -i 's/chr//' samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv
sed -i 's/cM_cox//' samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv
sed -i 's/Sample ID,//' samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv

#sed -n '1p' testing_df1.csv
#sed -n '2p' testing_df1.csv
#sed -n '3p' testing_df1.csv


head -n 1 samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv > 2_main_header.txt
sed -n '2p;3p;' samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv > 2_sub_header.txt #skip 4p b/c that is blank line

tail -n+5 samples_49_through_96_MURGIGV01_20180830_FinalReport_to_qtl_format.csv > 2_body.txt
paste -d"," <(echo "ID") 2_main_header.txt  > 2_final_main_header.txt







# check md5 to make sure the headers are the same
md5sum final_main_header.txt

md5sum 2_final_main_header.txt


cat final_main_header.txt sub_header.txt body.txt 2_body.txt > samples_1_to_96_genotypes_in_qtl_format.csv

# check number of fields is the same

awk -F"," '{print NF}' samples_1_to_96_genotypes_in_qtl_format.csv

# drop the last few samples since there is no phenotype info associated with it
head -n 94 samples_1_to_96_genotypes_in_qtl_format.csv > samples_1_to_91_genotypes_in_qtl_format_w_cM_positions.csv

