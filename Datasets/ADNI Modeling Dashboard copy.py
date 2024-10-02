# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:54:16 2024

@author: Marshall

This is going to be the script for our multipurpose file organizing GUI tool
"""
import importlib
import os
import pandas as pd
from scipy.spatial.distance import _METRICS #to choose which metric you want
import tkinter as tk
from tkinter import ttk
import Definition_Adder
importlib.reload(Definition_Adder) #always looks for updates no matter what


def add_labels():
    Definition_Adder.clean_them_all()
    feedback.delete(1.0, tk.END)  # Delete all existing text
    feedback.insert(tk.END, "Files Cleaned:\n")
    #pulls the list of files to clean from definition adder to put it in the feedback
    files_list_string = "\n".join(Definition_Adder.raw_files_list)
    feedback.insert(tk.END, files_list_string)
    
    #TODO make it so that the functions in the definition adder return feedback information about how the cleaning went
    #so that it can be displayed in the feedback text box

"""CREATE THE WINDOW"""

window = tk.Tk()
window.title("ADNI Modeling Dashboard - Your One Stop Shop for All Things ADNI")

#creates a notebook widget in the window aka the tab headings at the top of the page
tabs_menu = ttk.Notebook(window)
#creates multiple frame objects for the different tabs_menu that we will put widgets into
tab1 = ttk.Frame(tabs_menu)
tab2 = ttk.Frame(tabs_menu)
tab3 = ttk.Frame(tabs_menu)
#adds those two frames as tabs_menu to the notebook widget object
tabs_menu.add(tab1, text = "Collect Variables")
tabs_menu.add(tab2, text = "Create Domains")
tabs_menu.add(tab3, text = "Run Manifold")
#pack them in
tabs_menu.pack(expand=1, fill = "both")
#select the default tab
tabs_menu.select(tab2)

"""COLLECT VARIABLES TAB"""

#print the instructions on the page
instructions = "This page merges together all of our possible variables of interest for use"
tk.Label(tab1, text = instructions, wraplength=200).grid(column = 0, row = 0, padx = 10, pady = 10)
column_labels = ["Label", "Merge"]
for index, label in enumerate(column_labels):
    tk.Label(tab1, text = label, wraplength=200).grid(column = index + 1, row = 0, padx = 10, pady = 10)

#add the buttons to tab1
#put the add labels button on the page
add_labels_button = tk.Button(tab1, text="Add Definitions to Raw Datasets", command=lambda: add_labels())
add_labels_button.grid(column = 1, row = 1, padx = 10, pady = 10)
#put the merge buttons on the page
merge_profile_button = tk.Button(tab1, text="Merge Profile Variables", command=lambda: print("Merge Profile Variables"))
merge_profile_button.grid(column = 2, row = 1, padx = 10, pady = 10)
merge_visit_button = tk.Button(tab1, text="Merge Visit Variables", command=lambda: print("Merge Visit Variables"))
merge_visit_button.grid(column = 2, row = 2, padx = 10, pady = 10)
merge_progression_button = tk.Button(tab1, text="Merge Progression Variables", command=lambda: print("Merge Progression Variables"))
merge_progression_button.grid(column = 2, row = 3, padx = 10, pady = 10)
#put the feedback box at the bottom of the page
feedback1 = tk.Text(tab1, height=15, width=80) 
feedback1.grid(column = 1, row = 4, columnspan=4)

"""CREATE DOMAINS TAB"""

def get_files_list(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        print("Could not locate merged files")

#print the instructions on the page
instructions = "Select variables and distance metrics to generate domains for the manifold"
tk.Label(tab2, text = instructions, wraplength=200).grid(column = 0, row = 0, padx = 10, pady = 10)
column_labels = ["Select Merge", "Select Variables", "Select Distance Metric", "Generate"]
for index, label in enumerate(column_labels):
    tk.Label(tab2, text = label, wraplength=200).grid(column = index + 1, row = 0, padx = 10, pady = 10)
#put merge selector dropdown on the page
merged_files = get_files_list("Merged Data Files")
selected_merged_file = tk.StringVar()
selected_merged_file.set("Profile Variables 2024-08-21.xlsx") # Create a tk variable
distance_metric_dropdown = tk.OptionMenu(tab2, selected_merged_file, *merged_files)
distance_metric_dropdown.grid(row=1, column=1, padx=10, pady=10)

tk.Label(tab2, text = "All variables selected by default", wraplength=200).grid(column = 2, row = 1, padx = 10, pady = 10)

"""
finish this later, code for dynamically choosing variables within a canvassed checkbox menu, as completed by chatgpt response

#read in the merged file chosen for variable selection
excel_file = r"Merged Data Files/" + selected_merged_file.get()
sheet_name = 'Variable Catalog'
variables_df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=["Variable", "Nickname"])
#put in the variable selector
# Function to update the selection status
def update_selection():
    selected_items = [item for item, var in selected_vars.items() if var.get()]
    print(f"Selected items: {selected_items}")  # This could be processed further as needed

# Dictionary to keep track of the selected variables
selected_vars = {}

# Create a Checkbutton for each row in the DataFrame
for index, row in variables_df.iterrows():
    var = tk.BooleanVar(value=True)  # Default is checked (True)
    selected_vars[row["Variable"]] = var
    checkbutton = ttk.Checkbutton(
        tab2,
        text=f'{row["Variable"]}: {row["Nickname"]}',
        variable=var,
        command=update_selection
    )
    checkbutton.grid(row=1+index, column=2, padx=0, pady=0)
"""
#put the distance metric dropdown menu on the page
distance_metrics = list(_METRICS.keys())
distance_metrics.extend(["wrapped euclidean", "wrapped dtw", "use_rf_proximities"])
selected_distance_metric = tk.StringVar()
selected_distance_metric.set("euclidean") # Create a tk variable to store the selected option
distance_metric_dropdown = tk.OptionMenu(tab2, selected_distance_metric, *distance_metrics)
distance_metric_dropdown.grid(row=1, column=3, padx=10, pady=10)
#put the feedback box at the bottom of the page
feedback2 = tk.Text(tab2, height=15, width=80) 
feedback2.grid(column = 1, row = 300, columnspan=4) #get that sucker to the absolute bottom of the page

# Execute Tkinter
window.mainloop()