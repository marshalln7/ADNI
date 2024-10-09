# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 22:25:44 2024

@author: Marshall
"""

# Import necessary libraries
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix

import pandas as pd
import numpy as np

""" 
All functions here are made to accept a dataframe with the data columns that are to be used as
factors and a label series with all of the corresponding labels in it. It is expected that the
labels and indexers are already removed from the data dataframe
"""

def domain_validation(ADNI_dataset, model="random forest", feature_importance = False):
    """
    Fits the data to a random forest model and assembles all outputs into a string, that is then both
    printed and returned
    """
    print(f"Performing {model} validation on the provided dataset")
    
    data = ADNI_dataset.data
    feature_names = ADNI_dataset.variables
    label = ADNI_dataset.labels
    
    output_str = ""
    
    X_train, X_val, y_train, y_val = train_test_split(data, label, train_size=0.25, random_state=0)
    
    if model == "random forest":
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model == "k nearest neighbors":
        model = KNeighborsClassifier(n_neighbors=5)  # You can adjust the number of neighbors
        
    model.fit(X_train, y_train)
    
    # Perform cross-validation
    cross_val_scores = cross_val_score(model, X_train, y_train, cv=5)  # Using 5-fold cross-validation
    output_str += f'Mean cross-validation score: {cross_val_scores.mean()} \nStandard deviation of cross-validation scores: {cross_val_scores.std()}\n'
    
    # Perform permutation importance analysis to identify important factors
    if feature_importance == True:
        permutation_results = permutation_importance(model, X_val, y_val, n_repeats=30, random_state=0)
        for i in permutation_results.importances_mean.argsort()[::-1]:
            output_str += f"{feature_names[i]:<8} {permutation_results.importances_mean[i]:.3f} +/- {permutation_results.importances_std[i]:.3f}\n"
    
    # Use cross_val_predict to get predictions for each fold
    y_pred = cross_val_predict(model, X_train, y_train, cv=5)  # cv=5 means 5-fold cross-validation
    

    # Get the sorted unique labels used in the confusion matrix FIGURE OUT WHAT TO DO WITH THIS MAYBE LABELING
    # why aren't the numbers adding up for the labels and how are there any -4 missing labels?
    unique_labels = np.unique(np.concatenate([y_train, y_pred]))
    print(unique_labels)

    
    # Generate the confusion matrix
    conf_matrix = confusion_matrix(y_train, y_pred)
    output_str += f'Confusion matrix: \n{conf_matrix}\n'
    
    # Print and return the constructed string
    print(output_str)
    return output_str
    
class ADNI_Dataset:
    def __init__(self, dataframe, label_variable = "none"):
        #if an unindexed merged ADNI dataframe is fed into this with the label specified, it should do most of the organizational work for you
        print("Creating ADNI Dataset object...")
        self.labels = dataframe.pop(label_variable)
        try:
            self.rids = dataframe.pop("RID")
        except KeyError:
            print("Error, did you try to feed the ADNI Dataset object an indexed dataframe?")
        try: #tries to pull out the VISMONTH column, returns None if there isn't one
            self.vismonth = dataframe.pop("VISMONTH")
        except:
            self.vismonth = None
            
        dataframe = self.drop_object_columns(dataframe)
        
        self.variables = list(dataframe.columns)
        self.data = np.array(dataframe)
    
    def drop_object_columns(self, df):
        # Select columns with dtype 'object'
        object_cols = df.select_dtypes(include=['object']).columns
        # Print message showing deleted columns
        if not object_cols.empty:
            print(f"Deleted object-type columns: {', '.join(object_cols)}")
        else:
            print("No object-type columns found to delete.")
        # Drop the object-type columns
        df = df.drop(columns=object_cols)
        return df
        
    
if __name__ == "__main__":
    #iris = load_iris()
    # knn_validation(iris.data, iris.target)
    # rf_validation(iris.data, iris.target)
    
    #profile_df = pd.read_excel(r"Merged Data Files/Profile Variables 2024-09-13.xlsx").fillna(-4)
    visit_df = pd.read_excel(r"Merged Data Files/Visit Variables 2024-08-28.xlsx", nrows=None).fillna(-4)
    #scans_df = pd.read_excel(r"Merged Data Files/Scans 2024-8-19.xlsx", nrows=400)
    #rf_validation(profile.drop(["DX_bl", "PTRACCAT"], axis=1), profile.DX_bl)

    #profile = ADNI_Dataset(profile_df, label_variable="DX_bl")
    visit = ADNI_Dataset(visit_df, label_variable="DIAGNOSIS")
    #scans = ADNI_Dataset(scans_df, label_variable="DX_bl") #add more for this later where the permutation feature importance is skipped for a scans set
    domain_validation(visit, model="random forest", feature_importance=True)
    

    
