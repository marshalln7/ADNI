# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 17:04:09 2024

@author: Marshall
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Rows as Checkboxes")

        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(root, textvariable=self.dropdown_var)
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_file_selected)

        self.load_button = ttk.Button(root, text="Load Excel File", command=self.load_file)
        self.load_button.pack(pady=10)

        self.scrollable_frame = ScrollableFrame(root)
        self.scrollable_frame.pack(fill="both", expand=True)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.file_path = file_path
            self.update_dropdown()

    def update_dropdown(self):
        # Assuming there's only one sheet
        sheet_names = pd.ExcelFile(self.file_path).sheet_names
        self.dropdown['values'] = sheet_names

    def on_file_selected(self, event):
        selected_sheet = self.dropdown_var.get()
        df = pd.read_excel(self.file_path, sheet_name=selected_sheet)
        self.create_checkboxes(df)

    def create_checkboxes(self, df):
        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        self.check_vars = []

        for idx, row in df.iterrows():
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.scrollable_frame.scrollable_frame, text=f"Row {idx + 1}: {row.tolist()}", variable=var)
            cb.pack(anchor='w')
            self.check_vars.append(var)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
