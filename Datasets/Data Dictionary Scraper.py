# -*- coding: utf-8 -*-
"""
Created on Sat May  4 10:57:49 2024

@author: Marshall

Running this code takes a long time (about 15 minutes) but the result will be a 24066 by 6
dataframe with all of the possible data dictionary entries in it, sorted by table and 
exported as an excel file for subsequent use. The code does this by searching the online
data dictionary for each letter of the alphabet and concating the results.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import string

alphabet = list(string.ascii_lowercase)

def get_table(search_term):
    # URL of the webpage to scrape
    url = "https://adni.loni.usc.edu/data-dictionary-search/?q=" + search_term
    # Send a GET request to the URL
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table containing the data
        table = soup.find('table')
        
        # Extract table headers
        headers = [th.text.strip() for th in table.find_all('th')]
        
        # Extract table rows, ensuring the number of columns matches the number of headers
        data = []
        for tr in table.find_all('tr'):
            row = [td.text.strip() for td in tr.find_all('td')]
            if len(row) == len(headers):
                data.append(row)
        
        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data, columns=headers)
        
        # Print the DataFrame
        return df
    else:
        print("Failed to retrieve webpage.")

full_data_dictionary = None

for i in alphabet:
    print(i)
    df_new = get_table(i)
    full_data_dictionary = pd.concat([full_data_dictionary, df_new], axis=0).drop_duplicates()

#sort the values by table
full_data_dictionary = full_data_dictionary.sort_values(by="Table")

#export as an excel file
full_data_dictionary.to_excel("Full Offline Data Dictionary.xlsx", index=False)
