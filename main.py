"""
Main File takes inputs from commandline
"""
import allocate
import pandas as pd
import random
from data_ops import *
from output import *
time_slot=None
from shared import errors_dict, ROOM_ZONES,course_count # variable to understand which courses are throwing errors
seating_mode = None


# With time slots or specific course selection
def main(regdata_file_path, rooms_file_path):
    # Clean the registration data
    if not os.path.exists("data\\cleaned_erpdata.xlsx"): 
        regdata = clean_reg_data(regdata_file_path)
    else:
        regdata = pd.read_excel("data\\cleaned_erpdata.xlsx")

    print("Hi! Welcome to Seat Allocation Software for BITS Exams!")
    #incorporate date of exam

    global seating_mode, exam_title
    #Ask user which mode
    while True:
        exam_title = input("Enter which exam (Midsemester or Comprehensive) to generate seating arrangment for \n*NOTE: This will be reflected in all PDFs generated*: ")
        mode_choice = input(f"Choose seating arrangement for {exam_title}: (1) Serial Order (2) Random Order (3) Randomize in Zones (Enter 1 or 2 or 3): ").strip()
        if mode_choice == '1':
            seating_mode = "serial"
            break
        elif mode_choice == '2':
            seating_mode = "random"
            break
        elif mode_choice =='3':
            seating_mode = "random_zone"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    
    
    while True:
        # Ask the user for choice: Time slot or Course Number
        if os.path.exists("Output\\output_file.xlsx"):
            os.remove("Output\\output_file.xlsx")
        if os.path.exists("data\\room_status.csv"):
            os.remove("data\\room_status.csv")
        choice = input("Would you like to generate seating by (1) Time Slot, (2) Course Number, (3) All Courses on a Day, or (4) All Dates? (Enter 1, 2, 3, or 4): ").strip()
        
        room_data = pd.read_excel(rooms_file_path)
        
        if choice == '1':  # Generate by Time Slot
            date = validate_date()
            time_slot = validate_time_slot()
            
            if time_slot.lower() == "n":
                break
            
            courses_in_slot = room_data[(room_data['Date'] == date) & (room_data['Time'] == time_slot)]
            
            if courses_in_slot.empty:
                print(f"No courses found for this slot {date} & {time_slot}.")
                continue

            # Process each course in the selected time slot
            for _, course in courses_in_slot.iterrows():
                course_name = course['courseno']
                process_course(course_name, regdata, room_data, rooms_file_path, time_slot,date, seating_mode)
        
        elif choice == '2':  # Generate by Course Number
            course_name = validate_course_number()

            # Check if the course exists
            course_data = room_data[room_data['courseno'] == course_name].sort_values(by='courseno')
            if course_data.empty:
                print(f"No course found with the course number '{course_name}'.")
                continue

            # Get time slot for the specific course
            time_slot = course_data['Time'].values[0]
            date = course_data['Date'].values[0]
            process_course(course_name, regdata, room_data, rooms_file_path, time_slot,date, seating_mode)

        elif choice == '3':  # Generate for all courses on the given date
            date = validate_date()

            print(f"Generating seating arrangements for all courses on {date}.")

            # Filter courses based on the date
            #courses_on_date = room_data[room_data['Date'] == date].sort_values(by='courseno') #for sorted
            courses_on_date = room_data[room_data['Date'] == date]
            if courses_on_date.empty:
                print(f"No courses found on {date}.")
                continue

            # Print all courses on the date
            #print(courses_on_date[['courseno', 'Time']])

            # Sort courses by time to ensure morning courses are processed first
            morning_courses = []
            afternoon_courses = []
            
            for _, course in courses_on_date.iterrows():
                start_time = course['Time'].split(" - ")[0]
                if "AM" in start_time:
                    morning_courses.append(course)
                    
                else:
                    afternoon_courses.append(course)
                    
            
            # Process morning courses
            for course in morning_courses:
                course_name = course['courseno']
                time_slot = course['Time']
                process_course(course_name, regdata, room_data, rooms_file_path, time_slot,date,seating_mode)

            if os.path.exists("data\\room_status.csv"):
                os.remove("data\\room_status.csv")

            # Process afternoon courses
            for course in afternoon_courses:
                course_name = course['courseno']
                time_slot = course['Time']
                process_course(course_name, regdata, room_data, rooms_file_path, time_slot,date, seating_mode)

        elif choice == '4':  # Generate for all dates in data
            unique_dates = room_data['Date'].unique()
            for date in unique_dates:
                if os.path.exists("data\\room_status.csv"):
                    os.remove("data\\room_status.csv")
                print(f"\nProcessing all courses for date: {date}")

                courses_on_date = room_data[room_data['Date']==date].sort_values(by='courseno')
                if courses_on_date.empty:
                    continue
                
                morning_courses = []
                afternoon_courses = []

                for _, course in courses_on_date.iterrows():
                    start_time = course['Time'].split(" - ")[0]
                    if "AM" in start_time:
                        morning_courses.append(course)
                    else:
                        afternoon_courses.append(course)

                # Process morning courses
                for course in morning_courses:
                    course_name = course['courseno']
                    time_slot = course['Time']
                    process_course(course_name, regdata, room_data, rooms_file_path, time_slot,date, seating_mode)

                if os.path.exists("data\\room_status.csv"):
                    os.remove("data\\room_status.csv")

                # Process afternoon courses
                for course in afternoon_courses:
                    course_name = course['courseno']
                    time_slot = course['Time']
                    process_course(course_name, regdata, room_data, rooms_file_path, time_slot,date, seating_mode)

        elif choice =='n':
            save_errors()
            print("Errors encountered: ", errors_dict)
            print("Exiting the seating arrangement generator.")
            break
        else:
            print("Invalid input. Please enter 1, 2, 3 or 4.")
            continue

        # continuing
        save_errors()
        user_choice = input("Do you want to generate seating arrangement for another time slot or course number? (Y/N): ").strip().lower()
        if user_choice != 'y':
            print("Exiting the seating arrangement generator.")
            if os.path.exists("data\\room_status.csv"):
                    df = pd.read_csv("data\\room_status.csv")
                    print("Room Status CSV: \n", df)
                    os.remove("data\\room_status.csv")
            break
    
    print("Seat allocation completed.")

def process_course(course_name, regdata, room_data, rooms_file_path, time_slot, date, seating_mode):
    """Helper function to allocate seats and generate PDF for a specific course."""

    room_list = read_rooms(rooms_file_path, course_name)
    print("ROOM LIST", room_list)
    result = room_data[room_data['courseno'] == course_name]
    course_count = result['No. of students'].iloc[0] #total students to be seated in that course
    
    IC_name = result['IC'].values[0]
    Course_title = result['COURSE TITLE'].values[0]
    
    # Allocate seating and generate PDF for each course
    output = allocate.allocate(room_list, regdata, course_name, date,time_slot)
    #print(f"OUTPUT HEAD for serial seating arrangment:\n", output.head())
    if seating_mode == "random":
        output = shuffle_within_rooms(output) #random within rooms
        #print(f"OUTPUT HEAD for random seating arrangment:\n", output.head())
    elif seating_mode == "random_zone":
        output = shuffle_within_zones(output) #random within rooms

    
    create_pdf(output, time_slot, date, IC_name, Course_title,course_name, regdata, course_count, exam_title)     #regdata needed for course numbers - equivalent courses
    generate_room_pdfs(output, time_slot, date, IC_name, Course_title,course_name, course_count, exam_title)


def shuffle_within_rooms(df):
    """
    Shuffle students within each room while keeping Room and Seat Number fixed.
    """
    df_shuffled = df.copy()  # Create a copy to avoid modifying the original DataFrame

    # Group by 'Room' and shuffle each room separately
    def shuffle_group(group):
        student_cols = ['System ID', 'Email', 'Student Name', 'Student ID','Course']  # Columns to shuffle
        shuffled_students = group[student_cols].sample(frac=1, random_state=random.randint(0, 10000)).values
        group[student_cols] = shuffled_students  # Assign shuffled values back
        return group

    df_shuffled = df_shuffled.groupby('Room', group_keys=False).apply(shuffle_group).reset_index(drop=True)

    #print(df_shuffled.head())
    return df_shuffled

def assign_zones(df):
    """
    Assigns a zone to each row in the DataFrame based on the room-to-zone mapping.
    """
    def get_zone(room):
        for zone, room_list in ROOM_ZONES.items():
            if room in room_list:
                return zone
        return "Other"  # Default if room doesn't match any zone

    df["Zone"] = df["Room"].apply(get_zone)  # Apply zone mapping
    return df

def shuffle_within_zones(df):
    """
    Shuffle students within each zone while keeping Room and Seat Number fixed.
    """
    df = assign_zones(df)  # Ensure zones are assigned

    df_shuffled = df.copy()  # Create a copy to avoid modifying the original DataFrame

    # Group by 'Zone' and shuffle each group separately
    def shuffle_group(group):
        student_cols = ["Student ID", "Email", "Student Name"]  # Columns to shuffle
        shuffled_students = group[student_cols].sample(frac=1, random_state=random.randint(0, 10000)).values
        group[student_cols] = shuffled_students  # Assign shuffled values back
        return group

    df_shuffled = df_shuffled.groupby("Zone", group_keys=False).apply(shuffle_group).reset_index(drop=True)

    return df_shuffled


def save_errors():
    print("Errors encountered in the program", errors_dict)
    file_path = "errors_file.txt"
    # Writing dictionary to a text file
    with open(file_path, "w") as file:
        for key, value in errors_dict.items():
            file.write(f"{key}\n")
    

if __name__ == "__main__":
    reg_data_file_path = 'data\\erpdata.xlsx'
    rooms_file_path = 'data\\input-file-rooms.xlsx'
    main(reg_data_file_path, rooms_file_path)


