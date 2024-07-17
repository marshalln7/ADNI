# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:54:16 2024

@author: Marshall

This is going to be the script for our multipurpose file organizing GUI tool
"""

import tkinter as tk
from tkinter import ttk
import Definition_Adder


def clean_button():
    Definition_Adder.clean_them_all()
    feedback.delete(1.0, tk.END)  # Delete all existing text
    feedback.insert(tk.END, "Files Cleaned:\n")
    #pulls the list of files to clean from definition adder to put it in the feedback
    files_list_string = "\n".join(Definition_Adder.raw_files_list)
    feedback.insert(tk.END, files_list_string)
    
    #TODO make it so that the functions in the definition adder return feedback information about how the cleaning went
    #so that it can be displayed in the feedback text box

# creating Tk window
window = tk.Tk()
window.title("A Little App for Handling our ADNI Datasets")

#creates a notebook widget in the window aka the tab headings at the top of the page
tabControl = ttk.Notebook(window)
#creates multiple frame objects for the different tabs that we will put widgets into
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
#adds those two frames as tabs to the notebook widget object
tabControl.add(tab1, text = "Clean Stuff")
tabControl.add(tab2, text = "Merge Stuff")
tabControl.add(tab3, text = "Update Stuff")
#pack them in
tabControl.pack(expand=1, fill = "both")

#adds stuff to each of the tabs

#cleaning stuff tab
cleaning_instructions = "This button here will take all of the files in the Raw Data Files folder and create cleaned versions of them in the Nice Data Files folder"
tk.Label(tab1, text = cleaning_instructions, wraplength=200).grid(column = 0, row = 0, padx = 30, pady = 30)
tk.Button(tab1, text="Clean Files", command=lambda: clean_button()).grid(column = 1, row = 0, padx = 30, pady = 30)
feedback = tk.Text(tab1, height=15, width=80) 
feedback.grid(column = 1, row = 1)                                
                                                 
ttk.Label(tab2, text ="Let's dive into the world of computers, shall we? More to come here").grid(column = 0, row = 0, padx = 30, pady = 30)  


# Execute Tkinter
window.mainloop()