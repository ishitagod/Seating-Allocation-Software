"""
Main File takes inputs from commandline
"""
import allocate
from shared import *
from main_ops import *
from output import *
time_slot=None
seating_mode = None

# With time slots or specific course selection
def main(regdata_path, rooms_path, ics_path,
         exam_type, exam_title, seating_mode,
         output_mode, date=None, time_slot=None, course_name=None):
    # Clean the registration data
    if not os.path.exists("data\\cleaned_erpdata.xlsx"): 
        regdata = clean_reg_data(regdata_path)
    else:
        regdata = pd.read_excel("data\\cleaned_erpdata.xlsx")

    print("Hi! Welcome to Seat Allocation Software for BITS Exams!")
    #incorporate date of exam

    while True:
        # Ask the user for choice: Time slot or Course Number
        remove_output_file()
        remove_room_status()
        
        room_data = pd.read_excel(rooms_path)
        
        if output_mode == "time":  # Generate by Time Slot
            #date = validate_date()
            #time_slot = validate_time_slot()
            
            if time_slot.lower() == "n":
                break
            
            courses_in_slot = room_data[(room_data['Date'] == date) & (room_data['Time'] == time_slot)]
            
            if courses_in_slot.empty:
                print(f"No courses found for this slot {date} & {time_slot}.")
                continue

            # Process each course in the selected time slot
            for _, course in courses_in_slot.iterrows():
                course_name = course['courseno']
                process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)
        
        elif output_mode == 'course_number':  # Generate by Course Number
            #course_name = validate_course_number()

            # Check if the course exists
            course_data = room_data[room_data['courseno'] == course_name]  #.sort_values(by='courseno')
            if course_data.empty:
                print(f"No course found with the course number '{course_name}'.")
                continue

            # Get time slot for the specific course
            time_slot = course_data['Time'].values[0]
            date = course_data['Date'].values[0]
            process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)
            break
        elif output_mode == 'day':  # Generate for all courses on the given date
            #date = validate_date()

            print(f"Generating seating arrangements for all courses on {date}.")

            # Filter courses based on the date
            #courses_on_date = room_data[room_data['Date'] == date].sort_values(by='courseno') #for sorted
            courses_on_date = room_data[room_data['Date'] == date]
            if courses_on_date.empty:
                print(f"No courses found on {date}.")
                continue

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
                process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)


            remove_room_status()

            # Process afternoon courses
            for course in afternoon_courses:
                course_name = course['courseno']
                time_slot = course['Time']
                process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)
            break
        elif output_mode == 'all':  # Generate for all dates in data
            #how_generation = input("Generate all dates at once or one by one? Select 1 for all dates and 2 for one at a time:")
            if exam_type == 'midsem':#MIDSEM TIME SLOTS different
                unique_dates = room_data['Date'].unique()
                midsem_time_slots = room_data['Time'].unique()

                for date in unique_dates:
                    list_of_courses = []
                    remove_room_status()
                    print(f"\nProcessing all courses for date: {date}")

                    for time_slot in midsem_time_slots:
                        remove_room_status()
                        print(f"\nProcessing Time Slot: {time_slot}")
                        
                        # Filter courses for this specific date and time slot
                        courses_in_slot = room_data[
                            (room_data['Date'] == date) & (room_data['Time'] == time_slot)
                        ].sort_values(by='courseno')

                        if courses_in_slot.empty:
                            print(f"No courses found for {date} - {time_slot}. Skipping.")
                            continue

                        for _, course in courses_in_slot.iterrows():
                            course_name = course['courseno']
                            list_of_courses.append(course_name)
                            process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)

                        
                    if os.path.exists("data\\room_status.csv"):
                            df = pd.read_csv("data\\room_status.csv")
                            print("Room Status CSV: \n", df)
                            os.remove("data\\room_status.csv")
                            
                            print("✔ Cleared room status for next time slot.")
                   
                    print(f"Processing completed for {len(list_of_courses)} course(s): {', '.join(list_of_courses)}")
                    save_errors()
                    
                
            elif exam_type == 'comprehensive':#COMPRE TIME SLOTS different
                unique_dates = room_data['Date'].unique()
                for date in unique_dates:
                    remove_room_status()
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
                        process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)

                    remove_room_status()

                    # Process afternoon courses
                    for course in afternoon_courses:
                        course_name = course['courseno']
                        time_slot = course['Time']
                        process_course(course_name, regdata, room_data, rooms_path, ics_path,time_slot,date, seating_mode,exam_title)
        else:
            raise ValueError(f"Unknown output_mode: {output_mode}")
    
        save_errors()
        break    
    print("Seat allocation completed.")

def process_course(course_name, regdata, room_data, rooms_file_path, ics_file_path, time_slot, date, seating_mode,exam_title):
    """Helper function to allocate seats and generate PDF for a specific course."""

    room_list = read_rooms(rooms_file_path, course_name)
    result = room_data[room_data['courseno'] == course_name]
    course_count = result['No. of students'].iloc[0] #total students to be seated in that course
    
    IC_name = result['IC'].values[0]
    Course_title = result['COURSE TITLE'].values[0]
    
    # Allocate seating and generate PDF for each course
    output = allocate.allocate_rooms(room_list, regdata, course_name, date,time_slot)
    if seating_mode == "random":
        output = shuffle_within_rooms(output) #random within rooms
    elif seating_mode == "random_zone":
        output = shuffle_within_zones(output) #random within rooms

    create_pdf(output, time_slot, date, IC_name, Course_title,course_name, regdata, course_count, ics_file_path, exam_title)     #regdata needed for course numbers - equivalent courses
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

# if __name__ == '__main__':
#     print("Hello")
#     parser = argparse.ArgumentParser(description="Seat allocation runner")
#     parser.add_argument('regdata', help='Path to ERP registration data XLSX')
#     parser.add_argument('rooms', help='Path to Rooms-Exams XLSX')
#     parser.add_argument('ics', help='Path to ICs XLSX')
#     parser.add_argument('--exam_type', required=True, choices=['midsem','comprehensive'])
#     parser.add_argument('--exam_title', required=True, help='Title to show on PDFs')
#     parser.add_argument('--seating_mode', required=True, choices=['serial','random','random_zone'])
#     parser.add_argument('--output_mode', required=True, choices=['time','course_number','day','all'])
#     parser.add_argument('--date', help='Date if output_mode requires it (MM/DD/YYYY)')
#     parser.add_argument('--time_slot', help='Time slot if mode=time')
#     parser.add_argument('--course_number', help='Course number if mode=course_number')
#     args = parser.parse_args()

#     main(
#         regdata_file_path=args.regdata,
#         rooms_file_path=args.rooms,
#         ics_file_path=args.ics,
#         exam_type=args.exam_type,
#         exam_title=args.exam_title,
#         seating_mode=args.seating_mode,
#         output_mode=args.output_mode,
#         date_input=args.date,
#         time_slot=args.time_slot,
#         course_number=args.course_number
#     )

# def main(regdata_path, rooms_path, ics_path,
#          exam_type, exam_title, seating_mode, output_mode,
#          date=None, time_slot=None, course_number=None):
#     # Prepare regdata
#     cleaned = os.path.join('data', 'cleaned_erpdata.xlsx')
#     if not os.path.exists(cleaned):
#         regdata = clean_reg_data(regdata_path)
#     else:
#         regdata = pd.read_excel(cleaned)
#     room_data = pd.read_excel(rooms_path)

#     # Dispatch based on output_mode
#     def run_course(cno, ts, d):
#         process_course(cno, regdata, room_data, rooms_path, ics_path, ts, d, seating_mode, exam_title)

#     if output_mode == 'time':
#         for _, row in room_data[(room_data['Date']==date)&(room_data['Time']==time_slot)].iterrows():
#             run_course(row['courseno'], time_slot, date)
#     elif output_mode == 'course_number':
#         run_course(course_number, None, None)
#     elif output_mode == 'day':
#         for _, row in room_data[room_data['Date']==date].iterrows():
#             run_course(row['courseno'], row['Time'], date)
#     elif output_mode == 'all':
#         for _, row in room_data.iterrows():
#             run_course(row['courseno'], row['Time'], row['Date'])
#     else:
#         raise ValueError(f"Unknown mode: {output_mode}")

#     print("Seat allocation completed.")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('regdata')
    p.add_argument('rooms')
    p.add_argument('ics')
    p.add_argument('--exam_type', required=True)
    p.add_argument('--exam_title', required=True)
    p.add_argument('--seating_mode', required=True)
    p.add_argument('--output_mode', required=True)
    p.add_argument('--date')
    p.add_argument('--time_slot')
    p.add_argument('--course_number')
    args = p.parse_args()
    main(
      args.regdata, args.rooms, args.ics,
      args.exam_type, args.exam_title, args.seating_mode, args.output_mode,
      args.date, args.time_slot, args.course_number
    )


