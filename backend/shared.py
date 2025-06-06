#for shared variables
import pandas as pd
import os
import random
import re
from dotenv import load_dotenv
import os
import argparse
import sys
from datetime import datetime

load_dotenv()
ROOM_DATA_FOLDER = os.getenv("ROOM_DATA_FOLDER")
ROOM_STATUS_FILE_PATH = os.getenv("ROOM_STATUS_FILE_PATH")



def remove_output_file():
    if os.path.exists("Output\\output_file.xlsx"):
            os.remove("Output\\output_file.xlsx")
def remove_room_status():
      if os.path.exists("data\\room_status.csv"):
            os.remove("data\\room_status.csv")

#will add more later on! 
errors_dict = {}
#global
LT_names = ["LT1","LT2","LT3","LT4"]
DLT_names = ["DLT5","DLT6","DLT7","DLT8","DLT10"]
CC_lab = {
    'CCz1': "CC LAB-ZONE 1",
    'CCz2': "CC LAB-ZONE 2",
    'CCz3': ["CC LAB-ZONE 3A", "CC LAB-ZONE 3B"]
}
#Rooms to Zone mapping
ROOM_ZONES = {
    "DLT": ["DLT5", "DLT6", "DLT7", "DLT8", "DLT10"],
    "A50X": [f"A50{i}" for i in range(1, 9)],  # A501 to A508
    "A60X": [f"A60{i}" for i in range(1, 6)],  # A501 to A605
    "CC_Lab": ["CC LAB-ZONE 3B", "CC LAB-ZONE 3A", "CC LAB-ZONE 2","CC LAB-ZONE 1 "],
    "C30X": [f"C30{i}" for i in range(1, 9)],  # C301 to C308
    "C40X": [f"C40{i}" for i in range(1, 6)],  # C401 to C405
    "LT1_LT2": ["LT1", "LT2"],
    "LT3_LT4": ["LT3", "LT4"],
}

course_count=0


