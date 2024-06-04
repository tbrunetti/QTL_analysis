import pandas
import argparse
import os

def subset_illumina_final_report(final_report:str, snp_keep:str, snp_remove:str, sample_keep:str, sample_remove:str, outdir:str, file_prefix:str) -> None:

     # define snp and sample filtering fuctions
     def snp_filtering(inf_df) -> pandas.DataFrame:
          if snp_keep != None:
               keep_snp_list = []
               with open(snp_keep, 'r') as snps_to_keep:
                    for line in snps_to_keep:
                         keep_snp_list.append(line.strip())
               updated_snp_df = inf_df[inf_df['SNP Name'].isin(keep_snp_list)]
               return(updated_snp_df)
          elif snp_remove != None:
               remove_snp_list = []
               with open(snp_remove, 'r') as snps_to_remove:
                    for line in snp_remove:
                         remove_snp_list.append(line.strip())
               
               updated_snp_df = inf_df[~inf_df['SNP Name'].isin(remove_snp_list)]
               return(updated_snp_df)
     
     def sample_filtering(inf_df) -> pandas.DataFrame:
          if sample_keep != None:
               keep_sample_list = []
               with open(sample_keep, 'r') as samples_to_keep:
                    for line in samples_to_keep:
                         keep_sample_list.append(line.strip())
               print(keep_sample_list)
               updated_sample_df = inf_df[inf_df['Sample ID'].isin(keep_sample_list)]
               return(updated_sample_df)
          elif sample_remove != None:
               remove_sample_list = []
               with open(sample_remove, 'r') as samples_to_remove:
                    for line in samples_to_remove:
                         remove_sample_list.append(line.strip())

               updated_sample_df = inf_df[~inf_df['Sample ID'].isin(remove_sample_list)]
               return(updated_sample_df)
     
     # read in final report

     preheader_lines =  0
     with open(final_report, 'r') as ilmn_file:
          with open(os.path.join(outdir, file_prefix + '_snp_sample_filtered_final_report.txt'), 'w') as output_file: # since making new final report output preheader to that file
               for line in enumerate(ilmn_file):
                    output_file.write(line[1].strip() + '\n')
                    output_file.flush() # flush out buffer to maintain write orders
                    if line[1].strip() == "[Data]": # header starts after the line [Data] in the Illumina final report
                         preheader_lines = line[0]+1 # enumerate is 0-indexed but skip in pandas is 1-indexed
                         break


     inf_df = pandas.read_csv(filepath_or_buffer = final_report, sep = "\t", skiprows=preheader_lines, dtype=str)
     updated_snp_df = snp_filtering(inf_df = inf_df)

     updated_sample_df = sample_filtering(inf_df = updated_snp_df)

     # write filtered data back to final report
     updated_sample_df.to_csv(os.path.join(outdir, file_prefix + '_snp_sample_filtered_final_report.txt'), sep="\t", header = True, index= False, mode = 'a') # mode = a will append to existing file

     
def illumina_final_report_to_QTL_csv(final_report:str, cm_col_name:str, snp_map:str, file_prefix:str) -> None:
     '''
     snp_map = pandas.read_csv(filepath_or_buffer="/mnt/Gapin-Lab/For Tonya/B6_B:c_N2s_QTL_analysis/neogen_files/Univ_of_Colorado_Gapin_MURGIGV01_20180920/SNP_Map.txt", sep = "\t")
     updated_gigamuga_annots = pandas.read_csv("/home/tonya/bc_b6_backcross_gigamuga_array_03252024/gm_uwisc_v4.csv")
     snp_map.rename(columns={'Name': 'SNP Name'},inplace=True)
     updated_gigamuga_annots.rename(columns={'marker': 'SNP Name'}, inplace = True)

     snp_map_new_annots = snp_map.merge(updated_gigamuga_annots, on='SNP Name', how = "left")
     snp_map_new_annots = snp_map_new_annots[snp_map_new_annots['chr'].notna()] # keep only snps with chromsome w/o NaNs
     snp_map_new_annots = snp_map_new_annots[snp_map_new_annots['bp_mm10'].notna()] # keep only snps with chromsome w/o NaNs

     snp_map_new_annots['chr'] = snp_map_new_annots['chr'].astype(str)
     autosomal_snp_map = snp_map_new_annots.loc[snp_map_new_annots.chr.str.contains('^[1-9]')]
     autosomal_snp_map['chr'] = autosomal_snp_map['chr'].astype(int)
     autosomal_snp_map['bp_mm10'] = autosomal_snp_map['bp_mm10'].astype(int)
     autosomal_snp_map['cM_cox'] = autosomal_snp_map['cM_cox'].astype(float)

     autosomal_snp_map.sort_values(['chr', 'bp_mm10', 'cM_cox'],ascending=[True, True, True],inplace=True)
     '''
     preheader_lines =  0
     with open(final_report, 'r') as ilmn_file:
          for line in enumerate(ilmn_file):
               if line[1].strip() == "[Data]": # header starts after the line [Data] in the Illumina final report
                    preheader_lines = line[0]+1 # enumerate is 0-indexed but skip in pandas is 1-indexed
                    break

     
     inf_df = pandas.read_csv(filepath_or_buffer = final_report, sep = "\t", skiprows=preheader_lines)
     inf_df['genotype'] = inf_df['Allele1 - AB'] + inf_df['Allele2 - AB']
     snp_map_df = pandas.read_csv(filepath_or_buffer= snp_map, sep = '\t')
     inf_df_with_map = inf_df.merge(snp_map_df, on='SNP Name', how = "left")

     if cm_col_name != None:
          new_inf_df = inf_df_with_map.pivot(index = 'Sample ID',  columns= ['SNP Name','chr', cm_col_name], values= 'genotype')
          del inf_df_with_map
     else:
          new_inf_df = inf_df_with_map.pivot(index = 'Sample ID',  columns= ['SNP Name','chr'], values= 'genotype')
          del inf_df_with_map
     
     new_inf_df.to_csv(file_prefix + '_finalReport_to_qtl_format.csv', sep=",", header = True, index= True)


'''
Illumina Final Report Columns
 - SNP Name: name of SNP -- matches to Name column in SNP_Map.txt
 - Sample ID: sample name/sample ID       
 - Allele1 - Forward       
 - Allele2 - Forward        
 - Allele1 - Top   
 - Allele2 - Top   
 - Allele1 - AB    
 - Allele2 - AB    
 - GC Score
 - X
 - Y


 SNP_Map.txt columns
 - Index   - index of SNP, likely from BPM index
 - Name: SNP name that matches the SNP Name column in the Illumina Final Report
 - Chromosome: chromosome
 - Position: physical genomic position in base pairs relative to array probe genome version
 - GenTrain Score  
 - SNP : the SNP allele ex: [T/C], [A/T], [G/C], [C/A], etc...
 - ILMN Strand: 
 - Customer Strand 
 - NormID

 .lgen (pasted directly from plink website)
 A text file with no header line, and one line per genotype call (or just not-homozygous-major calls if 'lgen-ref' was invoked) usually with the following five fields:

Family ID
Within-family ID
Variant identifier (snp ID/snp name)
Allele call 1 ('0' for missing) [A, T, G, C or 0 for missing]
Allele call 2 [A, T, G, C or 0 for missing]

For us, Family ID and Within-family ID will be the same here and 


.fam file format
Sample information file accompanying a .bed binary genotype table. (--make-just-fam can be used to update just this file.) Also generated by "--recode lgen" and "--recode rlist".

A text file with no header line, and one line per sample with the following six fields:

    Family ID ('FID')
    Within-family ID ('IID'; cannot be '0')
    Within-family ID of father ('0' if father isn't in dataset)
    Within-family ID of mother ('0' if mother isn't in dataset)
    Sex code ('1' = male, '2' = female, '0' = unknown)
    Phenotype value ('1' = control, '2' = case, '-9'/'0'/non-numeric = missing data if case/control)

With the use of additional loading flag(s), PLINK can also correctly interpret some .fam files missing one or more of these fields.

If there are any numeric phenotype values other than {-9, 0, 1, 2}, the phenotype is interpreted as a quantitative trait instead of case/control status. In this case, -9 normally still designates a missing phenotype; use --missing-phenotype if this is problematic.

.map file format
A text file with no header line, and one line per variant with the following 3-4 fields:

    Chromosome code. PLINK 1.9 also permits contig names here, but most older programs do not.
    Variant identifier
    Position in morgans or centimorgans (optional; also safe to use dummy value of '0')
    Base-pair coordinate

'''


def illumina_final_report_to_plink(final_report: str, snp_map: str, file_prefix: str, bp_col_name: str, cm_col_name: str) -> None:
     '''
     TEST
     final_report = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/test_final_report.txt"
     snp_map = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/test_snp_map.txt"
     file_prefix= "test_prefix"
     '''


     def make_fam(final_report: pandas.DataFrame) -> None:
          samples = list(set(final_report["Sample ID"]))

          with open(file_prefix + '.fam', 'w') as fam_file:
               for id in enumerate(samples):
                    if id[0] != len(samples):
                         fam_file.write('\t'.join([str(id[1]), str(id[1]), '0', '0', '0', '0']) + '\n')
                         fam_file.flush()
                    else:
                         fam_file.write('\t'.join([str(id[1]), str(id[1]), '0', '0', '0', '0']))
                         fam_file.flush()                       
                         fam_file.close()

     def make_map(snp_map: pandas.DataFrame, bp_col_name:str, cm_col_name:str) -> None:
          '''
          TEST: 
          bp_col_name = 'bp_mm10'
          cm_col_name = 'cM_cox'
          '''

          if cm_col_name == None:
               snp_map['cM']  = 0
               snp_map[['Chromosome', 'SNP Name',  'cM',  bp_col_name,]].to_csv(file_prefix + '.map', sep = "\t", header = False, index = False)
          else:
               snp_map[['Chromosome', 'SNP Name',  cm_col_name,  bp_col_name,]].to_csv(file_prefix + '.map', sep = "\t", header = False, index = False)


     def make_lgen(final_report: pandas.DataFrame, file_prefix: str) -> None:
          lgen_format = final_report[['Sample ID', 'Sample ID', 'SNP Name', 'Allele1 - Forward', 'Allele2 - Forward']]
          lgen_format['Allele1 - Forward'].replace('-', '0', inplace = True)
          lgen_format['Allele2 - Forward'].replace('-', '0', inplace = True)
          lgen_format.to_csv(file_prefix + '.lgen', sep = '\t', index = False, header = False)


     preheader_lines =  0
     with open(final_report, 'r') as ilmn_file:
               for line in enumerate(ilmn_file):
                    if line[1].strip() == "[Data]": # header starts after the line [Data] in the Illumina final report
                         preheader_lines = line[0]+1 # enumerate is 0-indexed but skip in pandas is 1-indexed
                         break

     final_report = pandas.read_csv(final_report, sep = "\t", skiprows=preheader_lines)
     snp_map = pandas.read_csv(snp_map, sep = "\t")
     make_fam(final_report = final_report)
     make_map(snp_map = snp_map, bp_col_name = bp_col_name, cm_col_name = cm_col_name)
     make_lgen(final_report = final_report, file_prefix = file_prefix)

#def update_annotations_in_final_report(final_report:str, snp_map:str, updated_annots:str, autosomes_only:bool, output_new_snp_map:str, output_new_final_report:str) -> None:
def update_annotations_in_final_report(final_report:str, snp_map:str, updated_annots:str, autosomes_only:bool, file_prefix:str, outdir:str) -> None:

     '''
     TEST:
     final_report = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/Univ_of_Colorado_Gapin_MURGIGV01_20180920_FinalReport.txt"
     snp_map = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/SNP_Map_MURGIGV01_array_20180920.txt"
     updated_annots = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/gm_uwisc_v4.csv"
     autosomes_only = True
     output_new_snp_map = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/test_snp_map.txt"
     output_new_final_report = "/home/tonya/bc_b6_backcross_gigamuga_array_03252024/test_final_report.txt"
     '''


     preheader_lines =  0
     with open(final_report, 'r') as ilmn_file:
          with open(os.path.join(outdir, file_prefix + '_anno_updated_finalReport.txt'), 'w') as output_file: # since making new final report output preheader to that file
               for line in enumerate(ilmn_file):
                    output_file.write(line[1].strip() + '\n')
                    output_file.flush() # flush out buffer to maintain write orders
                    if line[1].strip() == "[Data]": # header starts after the line [Data] in the Illumina final report
                         preheader_lines = line[0]+1 # enumerate is 0-indexed but skip in pandas is 1-indexed
                         break

     
     final_report = pandas.read_csv(filepath_or_buffer = final_report, sep = "\t", skiprows=preheader_lines)
     snp_map = pandas.read_csv(filepath_or_buffer = snp_map, sep = "\t")
     updated_annots = pandas.read_csv(updated_annots)
     
     # update snp map column name to match final report
     snp_map.rename(columns={'Name': 'SNP Name'},inplace=True)
     # update annotation snp column name to match final report
     updated_annots.rename(columns={'marker': 'SNP Name'}, inplace = True)

     snp_map_new_annots = snp_map.merge(updated_annots, on='SNP Name', how = "left")
     snp_map_new_annots = snp_map_new_annots[snp_map_new_annots['chr'].notna()] # keep only snps with chromsome w/o NaNs
     snp_map_new_annots = snp_map_new_annots[snp_map_new_annots['bp_mm10'].notna()] # keep only snps with base pair positions lifted over to mm10 w/o NaNs

     # if autosomsal_only flag is set, then subsets snp map to only autosomal
     if autosomes_only: 
          snp_map_new_annots['chr'] = snp_map_new_annots['chr'].astype(str)
          autosomal_snp_map = snp_map_new_annots.loc[snp_map_new_annots.chr.str.contains('^[1-9]')]
          autosomal_snp_map['chr'] = autosomal_snp_map['chr'].astype(int)
          autosomal_snp_map['bp_mm10'] = autosomal_snp_map['bp_mm10'].astype(int)
          autosomal_snp_map['cM_cox'] = autosomal_snp_map['cM_cox'].astype(float)
          autosomal_snp_map.sort_values(['chr', 'bp_mm10', 'cM_cox'],ascending=[True, True, True],inplace=True)


          updated_final_report = final_report.merge(autosomal_snp_map, on='SNP Name', how = "right")
          updated_final_report[list(final_report)].to_csv(os.path.join(file_prefix + '_anno_updated_finalReport.txt'), sep="\t", header = True, index= False, mode = 'a') # mode = a will append to existing file
          autosomal_snp_map.to_csv(os.path.join(outdir, file_prefix + '_anno_updated_SNP_map.txt'), sep = "\t", header = True, index = False)

if __name__ == '__main__':
     import sys
     parser = argparse.ArgumentParser(description = 'function to help data wrangle genotyping data into commonly used genetic formats')
     parser.add_argument('--method', choices=['update_annots', 'reportToPlink', 'reportToQTLcsv', 'subsetReport'], help='Select one of the choice of what method/calculation you want to run')
     parser.add_argument('--finalReport', type=str, help = 'Full path to the Illumina final report generated by GenomeStudio')
     parser.add_argument('--snpMap', type = str, help = "Full path to the array snp map generated by GenomeStudio")
     parser.add_argument('--updateSnpMap', type = str, help = "Full path to the updated snp map annotations.  For formatting, please refer to gm_uwisc_v4.csv")
     parser.add_argument('--autosome', action='store_true', help = "If this flag is set, subset data to only autosomal chromosomes")
     parser.add_argument('--bpPosName', type = str, help = "The exact name of the column in your SNP Map that contain the physical base pair positions you want to use")
     parser.add_argument('--cMname', type = str, default=None, help = "The exact name of the column that contains the genetic cM distance for each marker.  This is optional.")
     parser.add_argument('--fileNamePrefix', type = str, help = 'A string of a file name prefix you want to use to name files.  Note, no file extensions needed and no spaces, special characters')
     parser.add_argument('--outDir', type = str, default=os.getcwd(), help = "Path or name of output directory; if it does not exist, one will be made" )
     # options below specific to function def subset_illumina_final_report()
     parser.add_argument('--snpKeep', type = str, default = None, help='A list of snp names to keep, 1 per line and snp name must be in the "SNP Name" column of the final report')
     parser.add_argument('--snpRemove', type = str, default= None, help='A list of snp names to remove, 1 per line and snp name must be in the "SNP Name" column of the final report')
     parser.add_argument('--sampleKeep', type = str, default = None, help='A list of sample names to keep, 1 per line and sample name must be in the "Sample ID" column of the final report.')
     parser.add_argument('--sampleRemove', type = str, default = None, help='A list of sample names to keep, 1 per line and sample name must be in the "Sample ID" column of the final report.')
     
     args = parser.parse_args()

     #TODO: check if directory exist, if not make it
     if os.path.isdir(args.outDir) == False:
          os.makedirs(args.outDir)

     
     if args.method == 'update_annots':
          # check if file with extenion for each function exists and if it does throw error; do not overwrite
          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '_SNP_map.txt')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '_SNP_map.txt')))
               sys.exit()
          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '_finalReport.txt')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '_finalReport.txt')))
               sys.exit()

          update_annotations_in_final_report(final_report = args.finalReport, snp_map = args.snpMap, updated_annots = args.updateSnpMap, \
                                        autosomes_only = args.autosome, file_prefix = args.fileNamePrefix, outdir=args.outDir)
     
     
     elif args.method == 'reportToPlink':
          # check if file with extenion for each function exists and if it does throw error; do not overwrite

          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '.map')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '.map')))
               sys.exit()
          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '.fam')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '.fam')))
               sys.exit()
          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '.lgen')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '.lgen')))
               sys.exit()

          illumina_final_report_to_plink(final_report = args.finalReport, snp_map = args.snpMap, file_prefix = args.fileNamePrefix, \
                                         bp_col_name = args.bpPosName, cm_col_name = args.cMname )
     elif args.method == 'reportToQTLcsv':
          # check if file generated from function exists and if it does throw error; do not overwrite
          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '_finalReport_to_qtl_format.csv')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '_finalReport_to_qtl_format.csv')))
               sys.exit()

          illumina_final_report_to_QTL_csv(final_report = args.finalReport, cm_col_name = args.cMname, snp_map = args.snpMap, file_prefix = args.fileNamePrefix)

     elif args.method == 'subsetReport':
          '''
          What should we be able to subset in a final report:
          1. list of SNPs to keep
          2. list of SNPs to remove
          3. list of samples to keep
          4. list of samples to remove
          '''
          # check if file generated from function exists and if it does throw error; do not overwrite
          try:
               assert os.path.exists(os.path.join(args.outDir, args.fileNamePrefix + '_snp_sample_filtered_final_report.txt')) == False
          except AssertionError:
               print('The file {} already exists.  Please select a new file prefix that does not exist in the output directory specified.'.format(os.path.join(args.outDir, args.fileNamePrefix + '_snp_sample_filtered_final_report.txt')))
               sys.exit()
          # TODO: keep and remove should be mutually exclusive for the same type
          subset_illumina_final_report(final_report = args.finalReport, snp_keep = args.snpKeep, snp_remove = args.snpRemove, sample_keep = args.sampleKeep, sample_remove = args.sampleRemove, outdir = args.outDir, file_prefix = args.fileNamePrefix)

