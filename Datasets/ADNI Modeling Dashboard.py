# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:54:16 2024

@author: Marshall

This script creates and manages the ADNI Dashboard interface. All merging, validating, and modeling functionalities
are handled externally and imported as seen below. The ultimate goal here is to create a class that an 
optimization algorithm can then use to create the optimum model
"""


import importlib
import os
import sys
import pickle
sys.path.insert(0, r"C:\Users\jcory\Box\Graph-Manifold-Alignment\Python_Files") #look for modules here as well

import pandas as pd
import numpy as np
from scipy.spatial.distance import _METRICS #to choose which metric you want
import tkinter as tk
from tkinter import ttk
import datetime

import Definition_Adder
import Profile_Variable_Merger
import Visit_Variable_Merger
import Progression_Variable_Merger
import Dataset_Validator
importlib.reload(Definition_Adder) #always looks for updates no matter what
importlib.reload(Profile_Variable_Merger)
importlib.reload(Visit_Variable_Merger)
importlib.reload(Progression_Variable_Merger)
importlib.reload(Dataset_Validator)

#from MASH import MASH
from mashspud import SPUD #used to reconstruct the triangular distance matricies that SPUD creates, see run_manifold()
from mashspud import triangular_helper as Triangular


class ADNI_Dashboard:
    def __init__(self, master):
        self.master = master
        
        self.buttons = {}  # Dictionary to store buttons before any tabs are created
        self.dropdowns = {} # Dictionary to store the dropdowns and what has been currently selected in [dropdown, selection] format
        self.checkboxes = {}  # Dictionary to store the checkboxes and if they are selected
        self.text_entries = {} # Dictionary to store small text or number entry boxes
        self.master.title("ADNI Modeling Dashboard - Your One Stop Shop for All Things ADNI")
        self.create_tabs() #sets up the different tabs and their corresponding pages
        
        
    def create_tabs(self):
        #creates a notebook widget in the window aka the tab headings at the top of the page
        tabs_menu = ttk.Notebook(window)
        
        #create and configure a style object for the background color
        color = "white"
        style = ttk.Style()
        style.configure("Custom.TFrame", background=color) #select your backg

        #the background image
        self.background_image = tk.PhotoImage(file="ADNI_transparent.png")
        
        #creates multiple frame objects for the different tabs_menu
        tab1 = ttk.Frame(tabs_menu, style="Custom.TFrame")
        tab2 = ttk.Frame(tabs_menu, style="Custom.TFrame")
        tab3 = ttk.Frame(tabs_menu, style="Custom.TFrame")
        
        # put widgets into them
        self.collect_variables_frame(tab1)
        self.create_domains_frame(tab2)
        self.run_manifolds_frame(tab3)
        
        #adds those two frames as tabs_menu to the notebook widget object
        tabs_menu.add(tab1, text = "Collect Variables")
        tabs_menu.add(tab2, text = "Create Domains")
        tabs_menu.add(tab3, text = "Run Manifolds")
        #place in grid
        tabs_menu.grid(row=0, column=0)
        #select the default tab
        tabs_menu.select(tab2)
        
        # Store the tabs and tabs_menu as attributes to use later
        self.tabs_menu = tabs_menu
        self.tab1 = tab1
        self.tab2 = tab2
        self.tab3 = tab3
    
    def get_files_list(self, directory):
        #gets a list of the files in a folder, usually for selection
        try:
            return [f for f in os.listdir(directory)]
        except FileNotFoundError:
            print("Could not locate merged files...")
    
    def on_variable_select(self, event):
        # Handles updating the current selection from a listbox into a string
        selected_indices = self.variable_listbox.curselection()
        self.deselected_vars = [self.variable_listbox.get(i) for i in selected_indices]
        print("Deselected Variables:", self.deselected_vars)  # Print or store the selection
    
    def add_background(self, frame):
        #hypothetically to add background images to each of the notebook pages, but I can't get it to work and so it isn't called
        background_label = tk.Label(frame, image=self.background_image, background="white")
        background_label.place(relx=0.45, rely=0.5, anchor="center", relwidth=1, relheight=1)  # Fill the entire frame
    
    def print_header(self, frame, column_labels):
        #prints any instructions and column labels across the top in a uniform way
        for index, label in enumerate(column_labels):
            tk.Label(frame, text = label, background = "white", wraplength=200).grid(column = index, row = 0, padx = 10, pady = 10)
    
    def create_button(self, frame, name, text, column, row, command):
        """Create a button with specified name and put it in the correct frame with the right text, position, and command"""
        button = tk.Button(frame, text=text, command=command, background="white")
        self.buttons[name] = button  # Store the button in the dictionary
        button.grid(column=column, row=row, padx=10, pady=10)

    def get_button(self, name):
        #Retrieve a button by its name from the dictionary.
        return self.buttons.get(name)
    
    def create_dropdown(self, frame, name, options, default, column, row, command=None):
        selection = tk.StringVar()
        selection.set(default) # Create a tk variable to store the selection
        dropdown = tk.OptionMenu(frame, selection, command=command,  *options)
        dropdown.config(bg="white", fg="black", activebackground="lightblue") # styling options, very cool
        dropdown.grid(column=column, row=row, padx=10, pady=10) # create and place the dropdown
        self.dropdowns[name] = [dropdown, selection] # store the object and its current selection in the dictionary
    
    def get_dropdown(self, name):
        #Retrieve a dropdown by its name from the dictionary.
        return self.dropdowns.get(name)
    
    def update_dropdown(self, name, new_options):
        # Clear the current options in the OptionMenu
        target_option_menu = self.dropdowns[name][0]
        selected_option = self.dropdowns[name][1]
        target_option_menu['menu'].delete(0, 'end')
        # Add new options to the OptionMenu
        for option in new_options:
            target_option_menu['menu'].add_command(label=option, command=tk._setit(selected_option, option))
        # Set the default value to the first new option
        selected_option.set(new_options[0])
    
    def create_checkboxes(self, frame, texts, default, column, startrow):
        for index, text in enumerate(texts): #make a checkbox for each text string recieved in the iterable texts arguement
            state = tk.BooleanVar()
            state.set(default) # Create a tk variable to store the selection
            checkbox = tk.Checkbutton(frame, text=text, variable=state, background="white")
            checkbox.grid(column=column, row=startrow+index, padx=10, pady=10)
            self.checkboxes[text] = [checkbox, state] # store the object and its current selection in the dictionary
        
    def get_checkbox(self, name):
        #Retrieve a dropdown by its name from the dictionary.
        return self.checkboxes.get(name)
    
    def create_text_entry(self, frame, name, text, default, column, row):
        #creates a text entry box with a label saying what it is packed into the same gridspace
        #Create a frame to hold the label and entry box
        small_frame = tk.Frame(frame, background="white")
        small_frame.grid(row=row, column=column, padx=5, pady=5)

        # Label inside the frame
        label = tk.Label(small_frame, text=text, background="white")
        label.pack(side='left')

        # Entry box inside the frame with default value of 10
        entry = tk.Entry(small_frame, width=5)
        entry.insert(0, default)
        entry.pack(side='left')
        self.text_entries[name] = [entry, entry.get()]
        
    
    def update_variable_selection(self, new_filename):
        print(new_filename)
        #import the data from the newly selected merge file
        self.merged_file_df = pd.read_excel(r"Merged Data Files/" + new_filename)
        self.variables_list = list(self.merged_file_df.columns)
        self.variables_list.remove("RID")
        # Clear the previous variable selection
        self.variable_listbox.delete(0, tk.END)
        # Add the new variable selection
        for variable_entry in self.variables_list:
            self.variable_listbox.insert(tk.END, variable_entry)
        self.print_feedback(self.feedback2, "Merge successfully selected, choose any variables that you'd like to exclude!")
            
    def print_feedback(self, text_widget, feedback):
        # Move the cursor to the end of the text in the widget
        text_widget.insert('end', feedback + '\n')
        # Scroll to the bottom to make sure the newly inserted feedback is visible
        text_widget.see('end')
    
    def add_labels(self):
        Definition_Adder.clean_raw_files()
        self.feedback1.delete("1.0", "end")  # Delete all existing text
        self.feedback1.insert("1.0", "Labels added to the following raw data files:\n")
        #pulls the list of cleaned files from definition adder to put it in the feedback
        files_list_string = "\n".join(Definition_Adder.raw_files_list)
        self.feedback1.insert("1.0", files_list_string)
    
    def merge_profiles(self):
        Profile_Variable_Merger.merge_profile_variables()
        self.update_dropdown(name = "merged_files", new_options = self.get_files_list("Merged Data Files"))
        
    def merge_visits(self):
        Visit_Variable_Merger.merge_visit_variables()
        self.update_dropdown(name = "merged_files", new_options = ["option1", "option2"])
        
    def merge_progressions(self):
        Progression_Variable_Merger.merge_progression_variables()
    
    def get_specified_dataframe(self):
        # this is a function for both the validation and distance matrix creation function to use to fetch the specified merge with the specified options
        # this function is meant to get all of its information from attributes of the ADNI_Dashboard class
        #gets all of the relevant selected settings for creating the distance matrix
        
        filename = self.dropdowns["merged_files"][1].get()
        df = pd.read_excel(r"Merged Data Files/" + filename)
        variable_types = pd.read_excel(r"Merged Data Files/" + filename, sheet_name="Variable Catalog")
        
        chosen_label = self.dropdowns["label"][1].get()
        onehot = self.checkboxes["Apply Onehot Encoding"][1].get()
        max_rid = int(self.text_entries["max_rid"][0].get())

        #all RIDs will be included up to the max rid
        df = df.loc[df['RID'] <= max_rid]
        #exclude deselected variables
        df.drop(self.deselected_vars, axis=1, inplace=True)
        variable_types = variable_types.loc[~variable_types['Variable'].isin(self.deselected_vars)]
        #does the onehot encoding
        if onehot == True:
            categorical_variables_list = list(variable_types.loc[variable_types["Type"] == "Categorical"].Variable)
            df = pd.get_dummies(df, dummy_na=True, columns=categorical_variables_list, dtype=float)
        
        print(df)
        return df
    
    def validate_domain(self):
        df = self.get_specified_dataframe().fillna(-4).set_index
        
    
    def create_distance_matrix(self):
        filename = self.dropdowns["merged_files"][1].get()
        df = self.get_specified_dataframe()
        chosen_label = self.dropdowns["label"][1].get()
        distance_metric = self.dropdowns["distance_metric"][1].get()
        
        #logic for getting rid of indexing or labeling columns and putting them together for the details file
        rids = pd.Series()
        vismonths = pd.Series()
        labels = pd.Series()
        
        if filename.startswith("Profile"): 
            rids = df.pop("RID")
            if chosen_label != "Not in dataset":
                labels = df.pop(chosen_label)
        elif filename.startswith("Visit"):
            rids = df.pop("RID")
            vismonths = df.pop("VISMONTH")
            if chosen_label != "Not in dataset":
                labels = df.pop(chosen_label)
        elif filename.startswith("Progression"):
            rids = df.RID.unique()
        elif filename.startswith("Scans"):
            rids = df.pop("RID")
            vismonths = df.pop("VISMONTH")
        
        variables = pd.Series(self.variables_list, name='Variables')
        rids = pd.Series(rids, name='RIDs')
        vismonths = pd.Series(vismonths, name='Vismonths')
        labels = pd.Series(labels, name='Labels')
        
        distances_info = pd.concat([variables,rids,vismonths,labels], axis=1)
        
        
        if filename.startswith("Progression") == False: #turn anything but progressions into an array
            data = df.to_numpy()
        else:
            data = df
            
        spud_object = SPUD(verbose=4)
        self.distance_matrix = spud_object.get_SGDM(data = data, distance_measure = distance_metric)
        print(self.distance_matrix)
        
        #export the triangular distance matrix to a pickle file and the options selected to an excel to be retrieved later
        
        now = datetime.datetime.now()
        datetime_string = now.strftime("%Y-%h-%d-@-%I-%M") # we shouldn't be using this too early or too late so we don't use army time, do %H to change it back
        new_filename = "_".join([filename[:-5], chosen_label, distance_metric, datetime_string])
        export_folder = "Distance Matricies\\" + new_filename
        os.makedirs(export_folder, exist_ok=True)
        
        with open(export_folder + "\\distances.pkl", 'wb') as triangular_export_file:
            pickle.dump(self.distance_matrix, triangular_export_file)
        
        # Use ExcelWriter to write the details to specific excel sheets
        with pd.ExcelWriter(export_folder + "//details.xlsx") as writer:
            distances_info.to_excel(writer, sheet_name='Details', index=False)
        
        feedback = f"The new distance matrix {new_filename} has been created and stored in the Distance Matricies folder!\nSee the folder and associated excel file for details."
        self.print_feedback(self.feedback2, feedback)
    
    
    def generate_anchors(self, domain1_folder, domain2_folder):
        # generates the list of two element lists that describe the two anchors between the domains from the details file
        details1 = pd.read_excel("Distance Matricies//" + domain1_folder + "//details.xlsx")
        details2 = pd.read_excel("Distance Matricies//" + domain2_folder + "//details.xlsx")
        
        anchors1 = details1.RIDs
        anchors2 = details2.RIDs
        
        anchors = []
        for i, rid1 in enumerate(anchors1):
            # Compare it with each item in list2
            for j, rid2 in enumerate(anchors2):
                # If they match, store the indices as a pair
                if rid1 == rid2:
                    anchors.append([i, j])
                    
        print(anchors)
        return anchors

    def run_manifold(self):
        # runs the manifold alignment based on the two domains selected and any other selected options
        
        # get the distance matricies to run
        domain1_folder = self.dropdowns["domain1"][1].get()
        domain2_folder = self.dropdowns["domain2"][1].get()
        with open("Distance Matricies//" + domain1_folder + "//distances.pkl", 'rb') as pickle_file:
            flat_distances = pickle.load(pickle_file)
            self.distances_1 = Triangular.reconstruct_symmetric(flat_distances)
        with open("Distance Matricies//" + domain2_folder + "//distances.pkl", 'rb') as pickle_file:
            flat_distances = pickle.load(pickle_file)
            self.distances_2 = Triangular.reconstruct_symmetric(flat_distances)
            
        # generate the appropriate anchors
        anchors = self.generate_anchors(domain1_folder, domain2_folder)
        
        self.print_feedback(self.feedback3, "Creating and fitting the SPUD object...")
        spud_object = SPUD(verbose=4, distance_measure_A="precomputed", distance_measure_B="precomputed")
        spud_object.fit(self.distances_1, self.distances_2, known_anchors=anchors)
        self.print_feedback(self.feedback3, "Fitting complete!")
        
        self.print_feedback(self.feedback3, "Generating selected visualizations, see your console for output")
    
    
    def collect_variables_frame(self, frame):
        #adds the background image
        self.add_background(frame)
        
        #instructions for the page
        instructions = "This page merges together all of our possible variables of interest for use"
        column_labels = [instructions, "Add Labels", "Create New Merges"]
        self.print_header(frame, column_labels)
        
        #put the feedback box at the bottom of the page
        self.feedback1 = tk.Text(frame, height=15, width=80) 
        self.feedback1.grid(column = 1, row = 300, columnspan=4)
        
        #put the add labels button on the page
        self.create_button(frame, "add_labels", "Add Definitions to Raw Datasets", column = 1, row = 1, command=self.add_labels)
        #put the merge buttons on the page
        self.create_button(frame, "merge_profile", "Merge Profile Variables", column = 2, row = 1, command=self.merge_profiles)
        self.create_button(frame, "merge_visit", "Merge Visit Variables", column = 2, row = 2, command=self.merge_visits)
        self.create_button(frame, "merge_progression", "Merge Progression Variables", column = 2, row = 3, command=self.merge_progressions)
        self.create_button(frame, "merge_profile_scan", "Merge Profile/Scan", column = 2, row = 4, command=None)
        self.create_button(frame, "merge_visit_scan", "Merge Visit/Scan ", column = 2, row = 5, command=None)
        
    
    def create_domains_frame(self, frame):
        #adds the background image
        self.add_background(frame)

        #print the instructions on the page
        instructions = "Select variables and distance metrics to generate domains for the manifold"
        column_labels = [instructions, "Select Merge", "Select Variables to Exclude", "Validate Domain", "Generate"]
        self.print_header(frame, column_labels)
        
        #put merge selector dropdown on the page
        merged_files_list = self.get_files_list("Merged Data Files")
        self.create_dropdown(frame=frame, name="merged_files", options=merged_files_list, default="Profile Variables 2024-08-21.xlsx", 
                             column=1, row=1, command=self.update_variable_selection)
        
        #selecting a sample size
        self.create_text_entry(frame, "max_rid", 'Enter the largest RID to include or "All":', "10", column=1, row=2)

        #appy onehot encoding or not
        self.create_checkboxes(frame,["Apply Onehot Encoding"], default=True, column=1, startrow=3)
        
        #Variable selector listbox with natural scrolling
        self.variable_listbox = tk.Listbox(frame, selectmode="multiple")
        self.variable_listbox.grid(column=2, row=1, rowspan=3)
        # Bind selection event
        self.variable_listbox.bind("<<ListboxSelect>>", self.on_variable_select)

        #validation method dropdown
        validation_methods = ["knn", "random forest"]
        self.create_dropdown(frame, "validation_method", validation_methods, "knn", column=3, row=1)
        
        #label dropdown
        labels = ["DX_bl", "Not in dataset"]
        self.create_dropdown(frame, "label", labels, "DX_bl", column=3, row=2)
        
        #validate domains button
        self.create_button(frame, "validate_domain", "Validate Domain", column = 3, row = 3, command=self.validate_domain)
        
        #put the distance metric dropdown menu on the page
        distance_metrics = list(_METRICS.keys())
        distance_metrics.extend(["wrapped euclidean", "wrapped dtw", "use_rf_proximities"])
        self.create_dropdown(frame, "distance_metric", distance_metrics, "euclidean", column=4, row=1)
        
        #create distance matrix
        self.create_button(frame, "create_distance_matrix", "Create Distance Matrix", column = 4, row = 2, command=self.create_distance_matrix)
        
        #put the feedback box at the bottom of the page
        self.feedback2 = tk.Text(frame, height=15, width=80) 
        self.feedback2.grid(column = 1, row = 300, columnspan=4) #get that sucker to the absolute bottom of the page

    
    def run_manifolds_frame(self, frame):
        #adds the background image
        self.add_background(frame)

        #print the instructions on the page
        instructions = "Select the domains and hyperparameters that you want to try to run the manifold"
        column_labels = [instructions, "Select Domains", "Select Hyperparameters", "Select Outputs", "Run"]
        self.print_header(frame, column_labels)
        
        distance_matrix_list = self.get_files_list("Distance Matricies")
        
        #domain 1 and 2 dropdowns
        self.create_dropdown(frame, "domain1", distance_matrix_list, "Select Domain 1", column=1, row=1)
        self.create_dropdown(frame, "domain2", distance_matrix_list, "Select Domain 2", column=1, row=2)
        
        #model choice dropdown
        models = ["MASH", "SPUD"]
        self.create_dropdown(frame, "model_selection", models, "SPUD", column=2, row=1)
        
        #Will put more model options here later
        text = "All defaults for the model are currently selected"
        tk.Label(frame, text = text, wraplength=200, background="white").grid(column = 2, row = 2, padx = 10, pady = 10)
        
        #select outputs using checkboxes
        possible_outputs = ["Heatmap", "Network", "Cross Embedding"]
        self.create_checkboxes(frame, possible_outputs, default = True, column=3, startrow=1)
        
        #run manifold button
        self.create_button(frame, "run_manifold", "Run Manifold!", column = 4, row = 1, command=self.run_manifold)
        
        #put the feedback box at the bottom of the page
        self.feedback3 = tk.Text(frame, height=15, width=80) 
        self.feedback3.grid(column = 1, row = 300, columnspan=4) #get that sucker to the absolute bottom of the page


if __name__ == "__main__":
    window = tk.Tk()
    window.iconbitmap('icon_2.ico')
    app = ADNI_Dashboard(window)
    window.mainloop()

# how to get just the FOSCTTM score from the spud class
# spud_class.FOSCTTM(spud_class.block[:self.len_A, self.len_A:]

# how to get the cross embedding score
# From sklearn.manifolds import MDS
# mds = MDS(n_comp = {The amount of features you have})
# Emb = Mds.fit(spud_class.block)
# spud_class.Cross_embedding(emb, (labels1, labels2))
