# EIFO Country Data Scraper

#### Project Description

This project is a Python-based web scraper designed to extract country-specific risk classification and cover policy data from the EIFO  website https://subdomain.eifo.dk/en/countries. The scraped data is then organized into a pandas DataFrame and saved as an Excel file for further analysis.

#### Two files:
scraper.py: The main Python script that performs the web scraping, processes the data, and saves it to an Excel file.
excel_outputs/: A directory where the output Excel files are saved.

#### Setup

Activate virtual environent `source venv/bin/activate` on mac-os

Necessary pip installations of packages are already included in venv. List of those required are at top of py file.

To run the script simply run: `python scraper.py`

Excel will be saved in "excel_outputs" folder.




