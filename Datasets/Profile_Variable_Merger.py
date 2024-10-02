# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:28:09 2024

@author: Marshall

This is a file that will generate a merged version of all of the profile variables currently selected
in the Profile Variables spreadsheet
"""

import pandas as pd
import numpy as np
import os
import sys
import datetime



def merge_profile_variables():
    #get a list of the available raw data files
    working_directory = os.getcwd()
    raw_files_list = os.listdir(working_directory + "\\Raw Data Files")
    
    #creates a dictionary of all of the profile variables to merge where the tables are keys and the values are lists of variables
    global profile_variables
    profile_variables = pd.read_excel("Profile Variables.xlsx")
    variables_to_merge = profile_variables.groupby('Table')['Variable'].apply(list).to_dict()
    #creates an index of the variable types (numerical, categorical, etc.) from the same table
    variable_types = profile_variables[["Variable", "Type"]].set_index("Variable")
    
    #keeps track of the variables that we have different entries for
    culpraits = []
    not_timeless = []
    
    #uncomment and edit this next row if you want to merge a custom set of variables
    #variables_to_merge = {"BIOMARK": ["BIBLOOD", "BIURINE"], "TOMM40": ["TOMM40_A1", "TOMM40_A2"]}
    
    print("Merging the variables:\n" + str(variables_to_merge))
    
    #starts creating the file to merge with with all of the RIDs from the roster
    merged_dataframe = pd.read_csv(working_directory + "\\Raw Data Files\\" + "ROSTER - Roster [ADNI1,GO,2,3,4].csv")
    merged_dataframe = merged_dataframe[["RID"]]
    merged_dataframe.drop_duplicates(inplace=True)
    
    def find_string_starting_with(strings, start):
        for string in strings:
            if string.startswith(start):
                return string
        sys.exit('Merge terminated, I was not able to find a file in the Raw Data Files folder with the code "' + start + '". Consider checking if the file is missing or not named correctly, or if the wrong table code was requested!')
    
    def apply_missing_data_protocols(df):
        #replace all of the active and passive null values with NaN
        null_values = [-1,-4, "-1", "-4", 9999, "9999"]
        df.replace(to_replace=null_values, value=np.nan, inplace=True)
        
    def has_conflicts(group):
        """ Check for conflicts within a group. """
        for col in group.columns:
            if col != 'ID':  # Skip the identifier columns
                unique_values = group[col].dropna().unique()
                if len(unique_values) > 1:
                    #TODO create a counter for the troublesome variables that shouldn't change but do and how many times they do
                    culpraits.append(group.iloc[0,0])
                    not_timeless.append(col)
                    return True
        return False
    
    def combine_rows(group):
        """ Combine rows if no conflicts, otherwise return rows as they are. """
        if len(group) == 1:
            return group
        elif has_conflicts(group):
            return group
        else:
            combined = group.iloc[0].copy()
            for col in group.columns:
                if col != 'ID':
                    combined[col] = group[col].dropna().iloc[0] if not group[col].dropna().empty else np.nan
            return pd.DataFrame([combined])
    
    #MERGE by opening each of the relevant tables as a dataframe and merges them into the merged_dataframe
    for table in variables_to_merge.keys():
        file_name = find_string_starting_with(raw_files_list, table)
        table_df = pd.read_csv(working_directory + "\\Raw Data Files\\" + file_name)
        table_df.sort_values(by="RID", inplace=True)
        #add the indexing variable to the list of variables to get from the table
        id = "RID"
        variables = variables_to_merge[table]
        variables.append(id)
        #apply missing data protocols and get rid of duplicates
        apply_missing_data_protocols(table_df)
        table_df.drop_duplicates(subset=variables, inplace=True)
        #get just the needed variables from the table
        needed_df = table_df[variables]
        #merges, and adds suffixes to the new merged variable names, but only if they are from different tables
        suffix = "_" + table
        merged_dataframe = merged_dataframe.merge(needed_df, on=id, how="left", suffixes=(None, suffix))
    
    #group together the rows that take no new information from each other
    merged_dataframe = merged_dataframe.groupby('RID', group_keys=False).apply(combine_rows)  
    
    #Iterates though the index of different variable types to set the numeric columns to numeric and 
    # the categorical columns to categorical
    for index, row in variable_types.iterrows():
        print(index)
        if row["Type"] == "Numerical":
            merged_dataframe[index] = merged_dataframe[index].astype("float")
        if row["Type"] == "Categorical":
            merged_dataframe[index] = merged_dataframe[index].astype("category")
        
    
    
    #TROUBLESHOOTING differing values for the same RIDs
    #print a little preview
    #print(merged_dataframe)
    #how many duplicate rows are we left with??? who are the culpriats and what are the problem variables??
    duplicate_rows = len(merged_dataframe.index) - merged_dataframe.nunique().iloc[0]
    print("Duplicate rows remaining before aggregation: " + str(duplicate_rows))
    print("These are their RIDs: " + str(culpraits))
    
    problem_variable_dict = {}
    for var in not_timeless:
        if var in problem_variable_dict:
            problem_variable_dict[var] += 1
        else:
            problem_variable_dict[var] = 1
    print("The problem variables are: " + str(problem_variable_dict))
    #creates a dataframe of all of the culpraits
    culpraits_frame = merged_dataframe[merged_dataframe["RID"].isin(culpraits)]
    
    
    #AGGREGATION of disagreeing values
    aggregation_functions = {
        'PTEDUCAT': 'max',  # Prefer the maximum value
        'PTHAND': 'first',  # Prefer the first non-NaN value
        'MOTHAD': 'max', #these 4 are binary of whether each parent had AD or Dementia, take the 1 if there is one
        'FATHAD': 'max',
        'MOTHDEM': 'max',
        'FATHDEM': 'max'
    }
    #any variables that aren't assigned a specific function in the dictionary above will be set to "first"
    unspecified_aggregation_functions = {var:'first' for var in merged_dataframe.columns if (var not in aggregation_functions) and (var != 'RID')}
    aggregation_functions.update(unspecified_aggregation_functions)
    #aggregate
    aggregated_dataframe = merged_dataframe.groupby('RID', as_index=False).agg(aggregation_functions)
    aggregated_dataframe.set_index("RID", inplace=True)
    aggregated_dataframe.sort_index(inplace=True)
    
    
    #REMAPPING selected variables
    #remapping dictionaries will store a dictionary where each variable is a key with a dictionary as the entry that records the remappings to do
    remapping_dictionaries = {'PTMARRY': {'Married': 1, 'Widowed': 2, 'Divorced': 3, 'Never married': 4, 'Unknown': -4, 'NaN': -4, -4: -4},
                              'DX_bl': {'CN': 0, 'SMC': 1, 'EMCI': 2, 'LMCI': 3, 'AD': 4, 'NaN': -4, -4: -4}}
    #does the remapping for each variable and stores the new mappings in profile_variables for the Variable Catalog tab
    profile_variables.set_index("Variable", inplace=True)
    for variable in remapping_dictionaries:
        aggregated_dataframe[variable] = aggregated_dataframe[variable].map(remapping_dictionaries[variable])
        profile_variables.at[variable, "Units"] = str(remapping_dictionaries[variable])
    profile_variables.reset_index(inplace=True)
    
    
    
    #PRUNING underdeveloped patients
    #Any patient that didn't make it far enough to get a baseline diagnosis is disqualified
    aggregated_dataframe = aggregated_dataframe.loc[~aggregated_dataframe["DX_bl"].isna()]
    
    
    #EXPORTING to a new merged file
    # Joining the strings of variables within each entry (minus the RID variable) with underscores for the file name
    id_less = lambda list: [variable for variable in list if variable != "RID"]
    joined_dict_entries = ['_'.join(id_less(list)) for list in variables_to_merge.values()]
    
    # Joining all the joined entries into one long string with underscores
    long_variables_string = '_'.join(joined_dict_entries)
    
    #export the new merged file to the Marged Data Files folder
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    new_filename = "Profile Variables " + date_string + ".xlsx"
    file_path = "Merged Data Files\\" + new_filename
    
    # Use ExcelWriter to write the merged data on the fist sheet and the variable catalog on the second
    with pd.ExcelWriter(file_path) as writer:
        aggregated_dataframe.to_excel(writer, sheet_name='Profile Variables', na_rep= "NaN")
        profile_variables.to_excel(writer, sheet_name='Variable Catalog', index=False)
    
    os.startfile(file_path)

if __name__ == "__main__":
    merge_profile_variables()