"""
This file is to clean the erp registration data recieved as an excel file and create a SQL database
with all the data for all exams.
"""
from shared import *

def clean_name(name):
    # Strip spaces, then remove any trailing characters that are not letters for IC names and folders
    cleaned_name = re.sub(r'[^\w\t]+', ' ', name)
    cleaned_name = re.sub(r'[^a-zA-Z]+$', '', name.strip())
    return cleaned_name

def clean_filename(name):
    """Sanitize the filename by cleaning up whitespaces and replacing special characters."""
    #ECE F341/ EEE F341/ INSTR F341 example
    
    # Replace all unusual whitespace (non-breaking, tabs, etc.) with a regular space
    name = re.sub(r'\s+', ' ', name.strip())
    # print("HELLO",name)
    # # Replace special characters `/`, `\` with `_`
    return name.replace("/", "_").replace("\\", "_")
