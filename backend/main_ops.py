
from shared import *
from datetime import datetime

def save_errors():
    print("Errors encountered in the program", errors_dict)
    file_path = "errors_file.txt"
    # Writing dictionary to a text file
    with open(file_path, "w") as file:
        for key, value in errors_dict.items():
            file.write(f"{key}\n")
    
def clean_reg_data(file_path):
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Define output path
    output_path = os.path.join(data_dir, 'cleaned_erpdata.xlsx')
    
    # Read input file
    df = pd.read_excel(file_path, skiprows=1, header=0)

    #from Grade In column remove DP, W and RC entries
    grades_to_remove = ['DP', 'W', 'RC']
   
    if 'Unit Taken' in df.columns:
        df = df[df['Unit Taken'] != 0]

    if all(col in df.columns for col in ['Subject', 'Catalog']):
        df['Subject_Catalog'] = df['Subject'].str.strip() +' '+ df['Catalog'].str.strip()
        df.drop(columns=['Subject', 'Catalog'], inplace=True)

    #Remove unnecessary columns
    #columns_to_remove = ['Semester', 'Career', 'Descr', 'Unit Taken', 'Grade In','Graded Component','Tutorial Section No','Project Section No','Thesis section']
    columns_to_remove = ['Semester', 'Career', 'Descr']
    columns = ['Campus ID','ID','Name',	'Email','Subject_Catalog']
    #df.drop(columns=columns_to_remove, axis=1, inplace=True)
    df=df[columns]
  
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



# def replace_error_files():