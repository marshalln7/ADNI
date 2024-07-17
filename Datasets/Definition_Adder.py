# -*- coding: utf-8 -*-
"""
Created on Mon May  6 15:11:04 2024

@author: Marshall
"""
import pandas as pd
import numpy as np
import os

working_directory = os.getcwd()
raw_files_list = os.listdir(working_directory + "\\Raw Data Files")
nice_files_list = os.listdir(working_directory + "\\Nice Data Files")

def clean_file(file):
    file_to_modify = "Raw Data Files/" + file
    official_data_dictionary = pd.read_csv("Official Data Dictionary.csv")
    scraped_data_dictionary = pd.read_excel("Scraped Data Dictionary.xlsx")
    
    target_dataset = pd.read_csv(file_to_modify)
    
    column_names = target_dataset.columns #the column names from the file of interest
    table_name = file_to_modify.split("/")[-1].split()[0] #grabs the code name for the table from the filename
    
    multi_index_list = []
    
    #keeps track of how many times both sets had an entry, how many times only the official set did,
    #how many times only the scraped set did, and how many times neither did
    error_tallies = [0,0,0,0]
    
    #function that takes the 0-4 different entries that apply to the variable and returns the best ones
    def find_rows_with_fewest_nans(df):
        # Select only the first three columns
        subset_df = df.iloc[:, :3]
        # Count the number of NaN values in each row
        nan_counts = subset_df.isnull().sum(axis=1)
        # Find the minimum number of NaN values
        min_nan_count = nan_counts.min()
        # Filter rows with the minimum number of NaN values
        rows_with_min_nans = df[nan_counts == min_nan_count]
        return rows_with_min_nans
    
    
    #VERY IMPORTANT NOTE: The data dictionary has seperate entries for the same variable
    #used on the same table but with multiple cohorts, sometimes with a few cohorts
    #listed in one entry and one listed in the other, and some that are missing
    #a definition even though other cohorts have them listed. This is a help, not a definitive source
    for variable in column_names:
        #retrieve data dictionary entries for the variable from both catalogs
        data_dictionary_entries = official_data_dictionary.loc[(official_data_dictionary.FLDNAME == variable) & (official_data_dictionary.TBLNAME == table_name)]
        supplemental_entries = scraped_data_dictionary.loc[(scraped_data_dictionary.Term == variable) & (scraped_data_dictionary.Table == table_name)]
        
        #the three pieces of informaton that we're trying to retrieve
        definition = "No def"
        code = "No code"
        units = "No units"
        
        #filter and change the column names to match
        filtered_official = data_dictionary_entries.loc[:,["FLDNAME", "TEXT", "CODE", "UNITS"]]
        filtered_official.columns = ["Term", "Definition", "Code", "Units"]
        filtered_supplemental = supplemental_entries.loc[:,["Term", "Definition", "Code"]]
        filtered_supplemental["Units"] = np.nan
        
        #some logic to decide which entries to use
        entry_options = pd.concat([filtered_official, filtered_supplemental], axis=0, ignore_index=True)
        
        #if there are any entries to use at all, get the most complete entries and use the first one
        if entry_options.empty == False:
            best_rows = find_rows_with_fewest_nans(entry_options)
            definition = best_rows.iloc[0]["Definition"]
            code = best_rows.iloc[0]["Code"]
            if data_dictionary_entries.empty == False:
                units = entry_options.iloc[0]["Units"]
        
        
        if (data_dictionary_entries.empty == False) & (supplemental_entries.empty == False):
            error_tallies[0] += 1
        elif (data_dictionary_entries.empty == False) & (supplemental_entries.empty == True):
            error_tallies[1] += 1
        elif (data_dictionary_entries.empty == True) & (supplemental_entries.empty == False):
            error_tallies[2] += 1
        elif (data_dictionary_entries.empty == True) & (supplemental_entries.empty == True):
            error_tallies[3] += 1
        
        if pd.isna(definition):
            definition = "No def"
        if pd.isna(code):
            code = "No code"
        if pd.isna(units):
            units = "No units"
        
        tuple_for_factor = (variable, definition, code, units)
        
        multi_index_list.append(tuple_for_factor)
    # Create a MultiIndex object
    multi_index = pd.MultiIndex.from_tuples(multi_index_list)
    
    # Create a DataFrame with the MultiIndex columns
    target_dataset.columns = multi_index
    
    #sub in a description for the -4 and -1 values (missing data protocals)
    #some of them are in as strings apparently, just something to be aware of with other numeric values
    target_dataset = target_dataset.replace(-4, "Not Taken")
    target_dataset = target_dataset.replace(-1, "Not There")
    target_dataset = target_dataset.replace("-4", "Not Taken")
    target_dataset = target_dataset.replace("-1", "Not There")
    
    target_dataset.to_csv("Nice Data Files/" + file, na_rep='NaN')

def clean_them_all():
    #makes a list of the files that haven't been cleaned already
    uncleaned_files = [file for file in raw_files_list if file not in nice_files_list]
    for file in uncleaned_files:
        clean_file(file)
    
    
    