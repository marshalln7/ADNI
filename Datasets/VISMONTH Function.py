# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:42:07 2024

@author: Marshall
"""

import pandas as pd
import numpy as np
import os
import sys
import datetime

from dateutil.relativedelta import relativedelta

working_directory = os.getcwd()
raw_files_list = os.listdir(working_directory + "\\Raw Data Files")

dataframe = pd.read_csv(working_directory + "\\Raw Data Files\\" + "REGISTRY - Registry [ADNI1,GO,2,3].csv")
baseline_dates = pd.read_csv(working_directory + "\\Raw Data Files\\" + "ADNIMERGE - Key ADNI tables merged into one table [ADNI1,GO,2,3].csv")
test_set = pd.read_csv(working_directory + "\\Raw Data Files\\" + "DXSUM PDXCONV - Diagnostic Summary [ADNI1,GO,2,3,4] - Copy.csv")

baseline_dates = baseline_dates[["EXAMDATE_bl", "RID"]].drop_duplicates()
baseline_dates.set_index("RID", inplace=True)



#TODO make this actually efficient and then add a bit to deal with those freaking ADNI3 visits
def create_VISMONTH_set(df):
    """
    This function will take any ADNI dataset with individual visits for rows, create a new column 
    for the number of months each visit was from the baseline visit, and fill that column with a correct
    number for each row if it's able to. If it can't, it will put a string in the original dataframe in place
    explaining why just in case you wanted to look through it. In the end it returns a new version with
    only the rows with a proper VISMONTH
    """
    
    #this could be shortened (it's just the code from the VISCODE2 transformation but it doesn't need to be so I might do that later
    def VISCODE1_transformation(row): 
        if str(row.VISCODE1).startswith("m"):
            return int(str(row.VISCODE2)[1:])
        elif row.VISCODE1 == "bl":
            return 0
        elif row.VISCODE1 == "f":
            return "failed screening"
        else:
            rid = row.RID
            
            # see if we have a baseline date from ADNIMERGE
            try: 
                their_baseline_date = baseline_dates.at[rid, "EXAMDATE_bl"]
                baseline_date_object = datetime.datetime.strptime(their_baseline_date, '%Y-%m-%d')
            except KeyError as e:
                print(f"KeyError: {e}. The RID {rid} does not have a baseline.")
                return "no baseline"
            # see if we have an EXAMDATE or VISDATE for the visit in quesiton, and try parsing it assuming different formats
            if "EXAMDATE" in df.columns:
                examdate = str(row.EXAMDATE)
                if examdate == "nan":
                    return "no examdate"
                else:
                    try:
                        visit_date_object = datetime.datetime.strptime(examdate, '%m/%d/%Y')
                    except ValueError:
                        visit_date_object = datetime.datetime.strptime(examdate, '%Y-%m-%d')
            elif "VISDATE" in df.columns:
                visdate = str(row.VISDATE)
                if visdate == "nan":
                    return "no visdate"
                else:
                    try:
                        visit_date_object = datetime.datetime.strptime(visdate, '%m/%d/%Y')
                    except ValueError:
                        visit_date_object = datetime.datetime.strptime(visdate, '%Y-%m-%d')
            
            #return the difference in months between the baseline and the visit in question
            difference = relativedelta(visit_date_object, baseline_date_object)
            months_difference = difference.years * 12 + difference.months + difference.days / 30
            return(months_difference)
        
    def VISCODE2_transformation(row):
        if str(row.VISCODE2).startswith("m"):
            return int(str(row.VISCODE2)[1:])
        elif row.VISCODE2 == "bl":
            return 0
        elif row.VISCODE2 == "f":
            return "failed screening"
        else:
            rid = row.RID
            
            # see if we have a baseline date from ADNIMERGE
            try: 
                their_baseline_date = baseline_dates.at[rid, "EXAMDATE_bl"]
                baseline_date_object = datetime.datetime.strptime(their_baseline_date, '%Y-%m-%d')
            except KeyError:
                return "no baseline"
            # see if we have an EXAMDATE or VISDATE for the visit in quesiton, and try parsing it assuming different formats
            if "EXAMDATE" in df.columns:
                examdate = str(row.EXAMDATE)
                if examdate == "nan":
                    return "no examdate"
                else:
                    try:
                        visit_date_object = datetime.datetime.strptime(examdate, '%m/%d/%Y')
                    except ValueError:
                        visit_date_object = datetime.datetime.strptime(examdate, '%Y-%m-%d')
            elif "VISDATE" in df.columns:
                visdate = str(row.VISDATE)
                if visdate == "nan":
                    return "no visdate"
                else:
                    try:
                        visit_date_object = datetime.datetime.strptime(visdate, '%m/%d/%Y')
                    except ValueError:
                        visit_date_object = datetime.datetime.strptime(visdate, '%Y-%m-%d')
            
            #return the difference in months between the baseline and the visit in question
            difference = relativedelta(visit_date_object, baseline_date_object)
            months_difference = difference.years * 12 + difference.months + difference.days / 30
            return(months_difference)
    
    #apply one of the two transformation functions from above
    if "VISCODE2" in df.columns:
        df["VISMONTH"] = df.apply(VISCODE2_transformation, axis=1)
    else:
        df["VISMONTH"] = df.apply(VISCODE1_transformation, axis=1)
    
    #filter out the rows with errors in the VISMONTH column
    #filtered_df = df[df['VISMONTH'].isnumeric() == True] #TODO find a reliable way to filter out the rows with error strings in them
    filtered_df = df[df['VISMONTH'].apply(lambda x: isinstance(x, int))]
    return filtered_df
        

new_dataframe = create_VISMONTH_set(dataframe)
new_test_set = create_VISMONTH_set(test_set)
