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

import pandas as pd
import numpy as np

""" 
All functions here are made to accept a dataframe with the data columns that are to be used as
factors and a label series with all of the corresponding labels in it. It is expected that the
labels and indexers are already removed from the data dataframe
"""

def rf_validation(dataframe, label):
    data = np.array(dataframe)
    feature_names = list(dataframe.columns)
    
    X_train, X_val, y_train, y_val = train_test_split(data, label, train_size=0.25, random_state=0)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Perform cross-validation
    cross_val_scores = cross_val_score(model, X_train, y_train, cv=5)  # Using 5-fold cross-validation
    
    # Perform permutation importance analysis to identify important factors
    permutation_results = permutation_importance(model, X_val, y_val, n_repeats=30, random_state=0)
    
    # Format the output nicely as a single string
    output_str = ""
    output_str += f'Mean cross-validation score: {cross_val_scores.mean()} \nStandard deviation of cross-validation scores: {cross_val_scores.std()}\n'
    for i in permutation_results.importances_mean.argsort()[::-1]:
        output_str += f"{feature_names[i]:<8} {permutation_results.importances_mean[i]:.3f} +/- {permutation_results.importances_std[i]:.3f}\n"
    
    # Print and return the constructed string
    print(output_str)
    return output_str
    

def knn_validation(dataframe, label):
    data = np.array(dataframe)
    feature_names = list(dataframe.columns)
    
    X_train, X_val, y_train, y_val = train_test_split(data, label, train_size=0.25, random_state=0)
    
    # Create the k-NN model
    knn_model = KNeighborsClassifier(n_neighbors=5)  # You can adjust the number of neighbors
    
    #fit the chosen model with all of the training data
    knn_model.fit(X_train, y_train)
    
    # Perform cross-validation
    cross_val_scores = cross_val_score(knn_model, X_train, y_train, cv=5)  # Using 5-fold cross-validation
    
    # Perform permutation importance analysis to identify important factors
    permutation_results = permutation_importance(knn_model, X_val, y_val, n_repeats=30, random_state=0)
    
    # Format the output nicely as a single string
    output_str = ""
    output_str += f'Mean cross-validation score: {cross_val_scores.mean()} \nStandard deviation of cross-validation cross_val_scores: {cross_val_scores.std()}\n'
    for i in permutation_results.importances_mean.argsort()[::-1]:
        output_str += f"{feature_names[i]:<8} {permutation_results.importances_mean[i]:.3f} +/- {permutation_results.importances_std[i]:.3f}\n"
    
    # Print and return the constructed string
    print(output_str)
    return output_str
    

    
if __name__ == "__main__":
    iris = load_iris()
    # knn_validation(iris.data, iris.target)
    # rf_validation(iris.data, iris.target)
    
    profile = pd.read_excel(r"Merged Data Files/Profile Variables 2024-09-13.xlsx", index_col="RID").fillna(-4)[:200]
    rf_validation(profile.drop(["DX_bl", "PTRACCAT"], axis=1), profile.DX_bl)
