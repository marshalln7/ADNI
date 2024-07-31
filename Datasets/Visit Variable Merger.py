# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 14:32:54 2024

@author: Marshall

This is a file that will generate the Visit Variables domain of our manifold based on the variables selected in
the Visit Variables spreadsheet
"""

import pandas as pd
import numpy as np
import os
import sys
import datetime
from dateutil.relativedelta import relativedelta


#get a list of the available raw data files
working_directory = os.getcwd()
raw_files_list = os.listdir(working_directory + "\\Raw Data Files")

#creates a dictionary of all of the timeless variables to merge where the tables are keys and the values are lists of variables
visit_variables = pd.read_excel("Visit Variables.xlsx")
variables_to_merge = visit_variables.groupby('Table')['Variable'].apply(list).to_dict()
print("Merging the variables:\n" + str(variables_to_merge))


#starts by creating an index by visit code and RID that we can merge everything else with
merged_dataframe = pd.read_csv(working_directory + "\\Raw Data Files\\" + "REGISTRY - Registry [ADNI1,GO,2,3].csv")
merged_dataframe = merged_dataframe[["RID", "VISCODE2"]]
merged_dataframe.set_index(["RID", "VISCODE2"]).sort_index(inplace = True)
merged_dataframe.drop_duplicates(inplace=True)

#get rid of the screenings because we don't care about them, if they fail there won't be any data
merged_dataframe = merged_dataframe[~merged_dataframe["VISCODE2"].isin(["sc", "f"])]

def find_string_starting_with(strings, start):
    for string in strings[::-1]:
        if string.startswith(start):
            return string
    sys.exit('Merge terminated, I was not able to find a file in the Raw Data Files folder with the code "' + start + '". Consider checking if the file is missing or not named correctly, or if the wrong table code was requested!')

def apply_missing_data_protocols(df):
    #replace all of the active and passive null values with NaN
    null_values = [-1,-4, "-1", "-4", 9999, "9999"]
    df.replace(to_replace=null_values, value=np.nan, inplace=True)
    
def ADAS_table():
    #okay so my thinking here is to create a merged ADAS table with all of the question and total scores put together
    #if a variable is called for that is not one of these variables, it will still be there
    #if one of the original ADASSCORES variables is called, it will be taken from the original table
    adas_adni1 = pd.read_csv(working_directory + "\\Raw Data Files\\" + "ADASSCORES - ADAS Sub-Scores and Total Scores [ADNI1].csv")
    adas_adniGo23 = pd.read_csv(working_directory + "\\Raw Data Files\\" + "ADAS - Alzheimer's Disease Assessment Scale (ADAS) [ADNIGO,2,3].csv")
    #rename the ADNI1 variables
    previous = ["VISCODE", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q14", "TOTALMOD"]
    new = ["VISCODE2", "Q1SCORE", "Q2SCORE", "Q3SCORE", "Q4SCORE", "Q5SCORE", "Q6SCORE", "Q7SCORE", "Q8SCORE", "Q9SCORE", "Q10SCORE", "Q11SCORE", "Q12SCORE", "Q13SCORE", "TOTAL13"]
    rename_dict = {previous[index]:new[index] for index in range(len(previous))}
    adas_adni1.rename(columns=rename_dict, inplace=True)
    adas_merged = pd.concat([adas_adni1, adas_adniGo23])
    return adas_merged

#read in each table with variables that we're interested in and merge in the variables
for table in variables_to_merge.keys():
    if table == "ADAS": #handling the weirdness of the ADAS tables
        table_df = ADAS_table()
    elif table == "UPENNBIOMK_MASTER":
        file_name = find_string_starting_with(raw_files_list, table)
        table_df = pd.read_csv(working_directory + "\\Raw Data Files\\" + file_name)
        table_df = table_df[table_df["BATCH"] == "MEDIAN"]
    else:
        file_name = find_string_starting_with(raw_files_list, table)
        table_df = pd.read_csv(working_directory + "\\Raw Data Files\\" + file_name)
    #add the indexing variables to the list of variables to get from the table
    id = "RID"
    #same tables, especially the ADNI1 tables, will only have VISCODE but in those cases VISCODE and VISCODE 2 are interchangable
    if "VISCODE2" in table_df.columns:
        visit = "VISCODE2"
    else:
        visit = "VISCODE"
    #the variables that we're interested in from the table
    variables = variables_to_merge[table]
    variables.append(id)
    variables.append(visit)
    #apply missing data protocols and get rid of irrelevant duplicates
    apply_missing_data_protocols(table_df)
    table_df.drop_duplicates(subset=variables, inplace=True)
    #get just the needed variables from the table
    needed_df = table_df[variables]
    #merges, and adds suffixes to the new merged variable names, but only if they are from different tables
    suffix = "_" + table
    merged_dataframe = merged_dataframe.merge(needed_df, left_on=[id, "VISCODE2"], right_on=[id, visit], how="outer", suffixes=(None, suffix))
    if visit == "VISCODE": #delete the extra visit code column if there is one
        merged_dataframe.drop(columns=['VISCODE'], inplace=True)

#set the baseline as month zero
merged_dataframe.VISCODE2.replace(to_replace="bl", value="m0", inplace=True)
#get rid of the screenings, the weird unsure visit and the mri visits for this domain
#also get rid of the new ADNI4 ones because they haven't published how the visit codes work yet
merged_dataframe = merged_dataframe[~merged_dataframe["VISCODE2"].isin(["sc", "uns1", "scmri", "4_bl", "4_sc", "4_disp", np.nan])]
# Extract visit month and create a new numeric column to store it
merged_dataframe['VISMONTH'] = merged_dataframe['VISCODE2'].str.extract('(\d+)').astype('Int64')
merged_dataframe.drop(columns='VISCODE2', inplace=True)
merged_dataframe.sort_values(by = ["RID", "VISMONTH"], inplace=True)
merged_dataframe.set_index(["RID", "VISMONTH"], inplace=True)

#export the new merged file to the Marged Data Files folder
now = datetime.datetime.now()
date_string = now.strftime("%Y-%m-%d")
new_filename = "Visit Variables " + date_string + ".xlsx"
file_path = "Merged Data Files\\" + new_filename

with pd.ExcelWriter(file_path) as writer:
    merged_dataframe.to_excel(writer, sheet_name='Visit Variables', na_rep= "NaN")
    visit_variables.to_excel(writer, sheet_name='Variable Catalog', index=False)

os.startfile(file_path)