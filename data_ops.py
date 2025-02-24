"""
This file is to clean the erp registration data recieved as an excel file and create a SQL database
with all the data for all exams.
"""
import pandas as pd
import re
from shared import errors_dict
from datetime import datetime

def clean_reg_data(file_path):
    df = pd.read_excel(file_path, skiprows=1, header=0) #change this when interface

    #from Grade In column remove DP, W and RC entries
    grades_to_remove = ['DP', 'W', 'RC']
    #df = df[df.get('Grade In', '').isin(grades_to_remove) == False]
    #print("START CHECK")
    #print(df.head())
    if 'Unit Taken' in df.columns:
        df = df[df['Unit Taken'] != 0]

    if all(col in df.columns for col in ['Subject', 'Catalog']):
        df['Subject_Catalog'] = df['Subject'].str.strip() +' '+ df['Catalog'].str.strip()
        df.drop(columns=['Subject', 'Catalog'], inplace=True)

    #print(df.head())
    #columns_to_check = ['Lecture Section No', 'Practical Section No', 'Tutorial Section No', 'Thesis section']
    
    # Drop rows where all the specified columns have NaN values
    #df = df.dropna(subset=columns_to_check, how='all')
    #df.drop(columns=['Lecture Section No'], inplace=True)
    #print(df.head())
    #subjects like PHY LAB have a practical section, cant remove
    # for col in ['Thesis section', 'Tutorial Section No', 'Project Section No']:
    #     if col in df.columns:
    #         df = df[df[col].isna()]

    #Remove unnecessary columns
    #columns_to_remove = ['Semester', 'Career', 'Descr', 'Unit Taken', 'Grade In','Graded Component','Tutorial Section No','Project Section No','Thesis section']
    columns_to_remove = ['Semester', 'Career', 'Descr']

    df.drop(columns=columns_to_remove, axis=1, inplace=True)

    #check dataframe
    #print(df.head())
    df.to_excel("data\\cleaned_erpdata.xlsx",index=False)
    return df


def read_rooms(file_name,course_name):
    # Read the course room details from the Excel file
    df = pd.read_excel(file_name)
    result = df[df['courseno'] == course_name]

    if result.empty:
        print(f"Course '{course_name}' not found.")

    if 'Room' in result.columns:
        rooms = result['Room'].values[0]
    elif 'Rooms' in result.columns:
        rooms = result['Rooms'].values[0]

    # Step 1: Extract room and capacity using regex
    room_capacity = re.findall(r'([A-Za-z0-9]+)\s*\((\d+)\)', rooms)
    room_capacity = [(room, int(capacity)) for room, capacity in room_capacity]
    # Step 2: Create a DataFrame
    df = pd.DataFrame(room_capacity, columns=["Rooms", "Capacity"])

    # Add a new column for courses
    df["Course"] = course_name

    # Convert capacity to integer
    df["Capacity"] = df["Capacity"].astype(int)

    # Step 3: Display the table
    #print("Room List\n",df)
    return df


def process_room_capacity(course_name, room_name, input_file_path="data/input-file-rooms.xlsx"):
    """
    Process room capacity from the input Excel file, expanding room and capacity information
    and aggregating capacities by Room, Date, and Time.
    
    Args:
        input_file_path (str): Path to the input Excel file.
        
    Returns:
        pd.DataFrame: A DataFrame containing aggregated capacities by Room, Date, and Time.
    """
    # Load the data from the input file
    data = pd.read_excel(input_file_path)
    # Expand rooms with capacities into separate rows
    rooms_expanded = (
        data.assign(Rooms=data['Rooms'].str.split(','))
        .explode('Rooms')
        .reset_index(drop=True)
    )

    # Split room and capacity
    
    rooms_expanded[['Room', 'Capacity']] = rooms_expanded['Rooms'].str.extract(r'([A-Za-z0-9]+)\s*\((\d+)\)')
    rooms_expanded['Capacity'] = rooms_expanded['Capacity'].astype(int) # Convert capacity to integer
    
    # Aggregate capacity by Room, Date, and Time
    aggregated_capacity = (
        rooms_expanded.groupby(['Room', 'Date', 'Time'])['Capacity']
        .sum()
        .reset_index()
    )
    
    course_data = data[data['courseno'] == course_name]
    time_slot = course_data['Time'].values[0]
    date = course_data['Date'].values[0]
    
    if room_name.lower() == "cc":
        cc_total_capacity = (
            aggregated_capacity[
                (aggregated_capacity['Room'].str.startswith('CC')) &
                (aggregated_capacity['Date'] == date) &
                (aggregated_capacity['Time'] == time_slot)
            ]['Capacity']
            .astype(int)
            .sum()
        )
        print("CC_TOTAL_CAPACITY",cc_total_capacity)
        return cc_total_capacity
        
    cap = aggregated_capacity[(aggregated_capacity['Room'] == room_name) & (aggregated_capacity['Time']==time_slot) & (aggregated_capacity['Date']==date)]['Capacity']

    return cap.iloc[0]

def clean_name(name):
    # Strip spaces, then remove any trailing characters that are not letters for IC names and folders
    cleaned_name = re.sub(r'[^\w\t]+', ' ', name)
    cleaned_name = re.sub(r'[^a-zA-Z]+$', '', name.strip())
    return cleaned_name

def clean_filename(name):
    """Sanitize the filename by replacing special characters with underscores."""
    #ECE F341/ EEE F341/ INSTR F341 example
    return name.replace("/", "_").replace("\\", "_")


def read_room_capacity(room_name, date, time_slot,file_name = "data\\input-file-rooms.xlsx"):
    """
    Calculate the total capacity for a specific room on a given date and time slot.
    """
    # Read the room details from the Excel file
    df = pd.read_excel(file_name)

    # Filter the DataFrame for the specified date, time slot, and room name
    result = df[(df['Date'] == date) & (df['Time'] == time_slot)]

    if result.empty:
        print(f"No entries found for Date '{date}', Time Slot '{time_slot}', and Room '{room_name}'.")
        return 0

    total_capacity = 0

    # Process each matching row to calculate capacity for the specific room
    for _, row in result.iterrows():
        rooms = row['Room'] if 'Room' in row else row['Rooms']
        extracted = re.findall(r'([A-Za-z0-9]+)\s*\((\d+)\)', rooms)
        
        for room, capacity in extracted:
            if room == room_name:
                total_capacity += int(capacity)

    return total_capacity


def validate_date():
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    while True:
        date = input("Please enter the date (DD/MM/YYYY, Day): ").strip()
        if "," not in date:
            print("Invalid format! Please include a comma and the day (e.g., '13/05/2024, Monday').")
            continue
        
        date_part, day_part = map(str.strip, date.split(",", 1))  # Split into date and day

        try:
            date_obj = datetime.strptime(date_part, "%d/%m/%Y")# Validate the date format
            actual_day = date_obj.strftime("%A")  # Get actual weekday

            # Check if the entered day matches the actual weekday
            if day_part not in days_of_week:
                print(f"Invalid day! Please enter a valid day like: {', '.join(days_of_week)}.")
                continue
            
            if day_part != actual_day:
                print(f"Incorrect day! {date_part} is actually a {actual_day}. Please enter the correct day.")
                continue

            return date  # If everything is valid, return the date
        
        except ValueError:
            print("Invalid date format! Please enter in 'DD/MM/YYYY, Day' format.")


def validate_time_slot():
    """Keep prompting the user until a valid time slot is entered in 'HH:MM AM/PM - HH:MM AM/PM' format."""
    time_pattern = r'^\d{1,2}:\d{2} [APM]{2} - \d{1,2}:\d{2} [APM]{2}$'
    while True:  # 🔹 Added loop for validation
        time_slot = input("Please enter the time slot (e.g., '10:00 AM - 11:30 AM'): ").strip()
        if re.match(time_pattern, time_slot):
            return time_slot  # If valid, return it
        print("Invalid time slot format! Please enter in 'HH:MM AM/PM - HH:MM AM/PM' format.")


def validate_course_number():
    """Keep prompting the user until a valid course number is entered in 'ABC G123' format or multiple courses separated by '/'."""
    course_pattern = r'^([A-Z]{2,5} [A-Z]\d{3})(?:\s*/\s*[A-Z]{2,5} [A-Z]\d{3})*$'
    
    while True:  # 🔹 Added loop for validation
        course_number = input("Please enter the course number (e.g., 'MEL G642' or 'ECON F354/ FIN F311'): ").strip()
        
        if re.match(course_pattern, course_number):
            return course_number  # If valid, return it
        
        print("Invalid course number format! Please enter in 'ABC G123' or 'ABC G123/ XYZ F456' format.")