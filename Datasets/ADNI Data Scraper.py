# -*- coding: utf-8 -*-
"""
Created on Mon May  6 14:40:22 2024

@author: Marshall

Doesn't scrape anything yet, but successfully logs into the ADNI database and accesses
one of the pages where all of the datasets are
"""

import requests
from bs4 import BeautifulSoup

# Authentication credentials
username = 'msn39@byu.edu'
password = 'EpsilonFiveFive5'

# Login URL
login_url = 'https://ida.loni.usc.edu/login.jsp'

# Create a session
session = requests.Session()

# Perform login
login_data = {
    'username': username,
    'password': password
}
response = session.post(login_url, data=login_data)

# Check if login was successful
if response.ok:
    # URL of the page to scrape after authentication
    url = 'https://ida.loni.usc.edu/pages/access/studyData.jsp'

    # Fetch the page after authentication
    response = session.get(url)

    # Parse HTML content
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data using BeautifulSoup
        # Example:
        # data = soup.find('div', class_='data-container').text
        # print(data)
        print("Access successful")
    else:
        print("Failed to fetch data page.")
else:
    print("Login failed.")
