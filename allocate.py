import pandas as pd
import os 
import re
from data_ops import process_room_capacity, read_room_capacity
from shared import errors_dict, LT_names, DLT_names, CC_lab

def load_cc_seating_arrangement(filepath):
    """ Load seating arrangement for each CC lab zone from the specified file, ignoring the serial column. """
    df = pd.read_excel(filepath, skiprows=1, usecols=[0, 2], header=None, names=['Zone', 'Seat'])
    # Filter and group seating arrangements by Zone, ignoring serial numbers
    cc_seat_mapping = {}
    df['Zone'] = df['Zone'].str.strip()
    for zone, seats in df.groupby('Zone')['Seat']:
        cc_seat_mapping[zone] = seats.tolist()  # Convert seat numbers to a list per zone

    #format is {'CC LAB-ZONE 1 ': [1, 3, 5, 7, 9....'CC LAB-ZONE 2 ': [1, 3, 6, 8, ...

    return cc_seat_mapping

def load_lt_seating_arrangement(filepath):
    """ Load the LT seating arrangement and capacity from the specified file path. """
    # Load the entire Excel sheet
    df = pd.read_excel(filepath, skiprows=0, header=None, names=['Serial', 'Seat'])
    
    # Get the capacity value from the second column of the first row (LT1, 66 in this case)
    capacity = df.iloc[0, 1]
    
    # Create a seating dictionary excluding the capacity row
    seating_dict = df.iloc[1:].set_index('Serial')['Seat'].to_dict()
    
    return seating_dict, capacity

def load_dlt_seating_arrangement(filepath):
    df = pd.read_excel(filepath, skiprows=0, header=None, names=['Serial', 'Seat'])
    
    # Get the capacity value from the second column of the first row (LT1, 66 in this case)
    capacity = df.iloc[0, 1]
    
    # Create a seating dictionary excluding the capacity row
    seating_dict = df.iloc[1:].set_index('Serial')['Seat'].to_dict()
    
    return seating_dict, capacity

def campus_id_key(id):
    """
    Generate a sorting key for campus IDs, handling multiple formats like 'A', 'B', 'H', and 'PH'.
    """
    year = int(id[:4])  # Extract the year
    primary_alpha = id[4]  # Determine the primary identifier ('A', 'B', 'H', 'P')

    if primary_alpha in ('A', 'B'):
        numeric_after_alpha = id[5]  # Extract numeric part after 'A' or 'B'
        secondary_alpha = ''
        secondary_numeric = None

        if primary_alpha == 'B':
            if id[7] == 'A':  # Check for secondary alpha after 'B'
                secondary_alpha = 'A'
                if id[8] == 'A':  # Handle 'AA' case
                    secondary_numeric = 'AA'
                else:
                    secondary_numeric = int(id[8]) if id[8].isdigit() else None
            else:
                secondary_numeric = (id[7])  # Direct number after 'B', like 'B5'

        ps_ts = id[6:8] if primary_alpha == 'A' else id[8:10]  # 'PS' or 'TS'
        ps_ts_priority = 0 if ps_ts == 'PS' else 1  # Prioritize 'PS' (0) over 'TS' (1)
        last_digits = int(id[-5:-1])  # Extract the last 4 digits

        return (
            year,
            primary_alpha,
            numeric_after_alpha,
            secondary_alpha,
            secondary_numeric if secondary_numeric is not None else '',
            ps_ts_priority,
            last_digits
        )

    elif primary_alpha == 'H':
        # Handle "H" type IDs
        # Check for variations within "H" type
        sub_category = id[5:8]  # Extract sub-category (e.g., '103', '106', '123')
        numeric_section = int(id[8:-1])  # Extract the numeric part
        return (year, primary_alpha, sub_category, numeric_section)

    elif primary_alpha == 'P' and id[5] == 'H':
        # Handle "PH" type IDs
        category = id[6:8]  # Extract 'RP' or 'XP'
        numeric_section = int(id[8:-1])  # Extract numeric part
        return (year, primary_alpha, category, numeric_section)

    else:
        # Catch-all for unsupported formats
        return (year, primary_alpha)



def allocate(rooms, students, course_name,date,time):
    """ Function to allocate room and seat number to students for the given course. """
    equivalent_course = False #Flag to help in future
    #For courses like EEE F244/ ECE F244/ INSTR F244
    #print(course_name)
    related_courses = [course.strip() for course in course_name.split('/ ')]
    #print(related_courses)
    if(len(related_courses)>1):
        equivalent_course = True

    course_students = students[students['Subject_Catalog'].isin(related_courses)]
    
    if course_students.empty:
        print("No students found for the exact course or related courses.")

    course_rooms = rooms[rooms['Course'] == course_name]
    #print("COURSE ROOMS:", course_rooms)
    seat_allocation = []
    #print(students['Subject_Catalog'])
    #print("CHECK THIS!\n",course_students)
    #print(course_rooms)

    #Initialize room status csv to store in time slot which rooms filled and which have more space
    update_room_csv()
    
    
    student_index = 0
    
    for _, room in course_rooms.iterrows():
        count_seats = 0
        room_name = room['Rooms']
        
        assigned_capacity = room['Capacity']
        print(room_name,":",assigned_capacity)
        #redundant for LT, DLT and CC Lab because of hard & soft limits, useful to check if number of seats accurate acc to assignment given
        #for A & C because overlapping courses and 

        classes_df = pd.read_excel(r"data\room_data\Classrooms.xlsx", skiprows=1, header=None, names=['Room Name', 'Capacity'])
        filled_seats=0

        room_status = read_room_status(room_name=room_name)
        room_status_df = pd.read_csv("data\\room_status.csv")

        if room_status is not None:
            # Extract capacity and filled seats
            filled_seats = room_status['Filled Seats'].values[0]
        
        # Determine room type and handle LT rooms with two different seating capacities
        if room_name.startswith('LT'):
            #CHECK IF EXISTS IN ROOM_STATUS CSV IF IT DOES READ THE SOFT/HARD LIMIT PART AND SORT ACCORDINGLY FOR THE REST
            lt_soft_path = f"data\\room_data\\{room_name}_SoftLimit.xlsx"
            lt_hard_path = f"data\\room_data\\{room_name}_HardLimit.xlsx"
            
            lt_soft_seats,soft_cap = load_lt_seating_arrangement(lt_soft_path)
            lt_hard_seats,hard_cap = load_lt_seating_arrangement(lt_hard_path)
            
            
            aggregated_capacity_room = read_room_capacity(room_name,date,time)
            print("Full Capacity of Room:", aggregated_capacity_room)

            room_stat_df = read_room_status(room_name=room_name)
            if room_stat_df is not None:
                filled_seats = room_stat_df.loc[room_stat_df['Room Name']==room_name,"Filled Seats"].values[0]
                lt_limit_type = room_status_df.loc[room_status_df['Room Name'] == room_name, 'Limit Type'].values[0]
                if (lt_limit_type == "Soft"):
                     lt_seats = lt_soft_seats 
                     lt_cap = soft_cap
                else:
                    lt_seats = lt_hard_seats
                    lt_cap = hard_cap
            #lt_seats {1: 21, 2: 26, 3: 27, 4: 30...}
            else:
                if int(aggregated_capacity_room) <= soft_cap:
                    lt_seats = lt_soft_seats 
                    lt_limit_type = "Soft" 
                else:
                    lt_seats = lt_hard_seats
                    lt_limit_type = "Hard"
            
            for seat_number in range(filled_seats+1, len(lt_seats)+1):
                #print(seat_number,filled_seats)
                if(count_seats>=assigned_capacity):
                    update_room_csv(room_name=room_name, capacity= aggregated_capacity_room,filled_seats=seat_number-1,limit_type=lt_limit_type)
                    count_seats=0
                    break
                elif ((student_index >= len(course_students))|(seat_number>aggregated_capacity_room)): #check if assigned capacity fulfilled
                    #print("BROKEN!")
                    #print(room_name,aggregated_capacity_room,seat_number,lt_limit_type)
                    update_room_csv(room_name=room_name, capacity= aggregated_capacity_room,filled_seats=seat_number-1,limit_type=lt_limit_type)
                    count_seats=0
                    
                    #print("check1",student_index,len(course_students))
                    #print("check2",seat_number>assigned_capacity)
                    break
                
                actual_seat = lt_seats.get(seat_number, seat_number)
                #print("filled seats ",filled_seats,"seat num ", seat_number)
                #print("actual seat ",actual_seat)
                student = course_students.iloc[student_index]
                
                seat_allocation.append({
                    'System ID' : student['ID'],
                    'Email':student['Email'],
                    'Student Name': student['Name'],
                    'Student ID': student['Campus ID'],
                    'Course': student['Subject_Catalog'],
                    'Room': room_name,
                    'Seat Number': actual_seat
                })
                student_index += 1
                count_seats+=1
                filled_seats+=1
                update_room_csv(room_name=room_name, capacity= aggregated_capacity_room,filled_seats=filled_seats,limit_type=lt_limit_type)
        
        elif room_name.startswith('DLT'):   
            dlt_path = f"data\\room_data\\{room_name}.xlsx"
            dlt_seats, dlt_cap = load_dlt_seating_arrangement(dlt_path)
            
            aggregated_capacity_room = read_room_capacity(room_name,date,time)
            #print("Full Capacity of Room:", aggregated_capacity_room)
            #print("aggregated capacity:", aggregated_capacity_room)

            room_stat_df = read_room_status(room_name=room_name)

            if room_stat_df is not None:
                filled_seats = room_stat_df.loc[room_stat_df['Room Name']==room_name,"Filled Seats"].values[0]
    
            #print(dlt_seats)
            for seat_number in range(filled_seats+1, len(dlt_seats)+1):
                if ((student_index >= len(course_students))|(seat_number>aggregated_capacity_room)):
                    update_room_csv(room_name=room_name, capacity= aggregated_capacity_room,filled_seats=seat_number-1,limit_type=" ")
                    count_seats=0
                    break
                actual_seat = dlt_seats.get(seat_number, seat_number)
                #print("filled seats ",filled_seats,"seat num ", seat_number)
                #print("actual seat ",actual_seat)
                student = course_students.iloc[student_index]
                seat_allocation.append({
                    'System ID' : student['ID'],
                    'Email':student['Email'],
                    'Student Name': student['Name'],
                    'Student ID': student['Campus ID'],
                    'Course': student['Subject_Catalog'],
                    'Room': room_name,
                    'Seat Number': actual_seat
                })
                student_index += 1
                count_seats +=1
                update_room_csv(room_name=room_name,capacity= aggregated_capacity_room,filled_seats=filled_seats+count_seats,limit_type=" ")

        elif room_name.startswith('CC'):
            # Load CC lab seating arrangement based on total capacity

            #cc_total_capacity = course_rooms[course_rooms['Rooms'].str.startswith('CC')]['Capacity'].sum()
            
            cc_total_capacity = process_room_capacity(course_name,"cc")
            cc_total_capacity=int(cc_total_capacity)
            #print("CC total capacity for time and day: ",cc_total_capacity)
            cc_filepath = "data\\room_data\\CCLab_HardLimit.xlsx" if cc_total_capacity > 202 else "data\\room_data\\CCLab_SoftLimit.xlsx"
            cc_seat_mapping = load_cc_seating_arrangement(cc_filepath)

            #number of filled seats from room_status.csv
            

            # Handle CC rooms using specific zones and seating arrangement
            zone_keys = CC_lab[room_name]  # Get zone(s) associated with this CC room
            # print("zone keys",zone_keys)
            # print("hello", cc_seat_mapping)
            if isinstance(zone_keys, list):
                
                # Process for rooms with multiple zones (e.g., CCz3 with "CC LAB-ZONE 3A" and "CC LAB-ZONE 3B")
                for zone in zone_keys:
                    # Strip the last alphabet from the zone name
                    stripped_zone = zone[:-1] if zone[-1].isalpha() else zone
                    #print("zone: ",zone)
                    room_stat_df = read_room_status(room_name=stripped_zone)
                    if room_stat_df is not None:
                        filled_seats = room_stat_df.loc[room_stat_df['Room Name']==stripped_zone,"Filled Seats"].values[0]
                        #print("filled",filled_seats)
                    else:
                        filled_seats = 0


                    seat_numbers = cc_seat_mapping.get(zone, [])
                    #print("MAPPING",seat_numbers)
                    if(zone == "CC LAB-ZONE 3B"): 
                        room_stat_df = read_room_status(room_name=zone)
                        if room_stat_df is not None:
                            filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone,"Filled Seats"].values[0]
                        else:
                            filled_seats = 0
                    
                    for seat_number in range(filled_seats,len(seat_numbers)):
                        if student_index >assigned_capacity:
                            break
                        elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                            break
                        student = course_students.iloc[student_index]
                        seat_allocation.append({
                            'System ID' : student['ID'],
                            'Email':student['Email'],
                            'Student Name': student['Name'],
                            'Student ID': student['Campus ID'],
                            'Course': student['Subject_Catalog'],
                            'Room': zone,  # Updated room name to reflect the exact zone
                            'Seat Number': seat_numbers[seat_number]
                        })
                        student_index += 1
                        filled_seats += 1
                        
                    update_room_csv(room_name=stripped_zone, capacity=cc_total_capacity, filled_seats=filled_seats)  # Update room status with exact zone name
                    update_room_csv(room_name=zone, capacity=assigned_capacity, filled_seats=filled_seats)
            else:
                # Process for rooms with a single zone (e.g., CCz1 or CCz2)
                #print("WE WENT TO ELSE STATEMENT! CC")
                seat_numbers = cc_seat_mapping.get(zone_keys)
                room_stat_df = read_room_status(room_name=zone_keys)
                if room_stat_df is not None:
                        filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone_keys,"Filled Seats"].values[0]
                        #print("filled IN ELSE",filled_seats)
                for seat_number in range(filled_seats,len(seat_numbers)):
                    if student_index >assigned_capacity:
                        break
                    elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                        break
                    student = course_students.iloc[student_index]
                    seat_allocation.append({
                        'System ID' : student['ID'],
                        'Email':student['Email'],
                        'Student Name': student['Name'],
                        'Student ID': student['Campus ID'],
                        'Course': student['Subject_Catalog'],
                        'Room': zone_keys,  # Updated room name to reflect the exact zone
                        'Seat Number': seat_numbers[seat_number]
                    })
                    student_index += 1
                    filled_seats += 1
                update_room_csv(room_name=zone_keys, capacity=assigned_capacity, filled_seats=filled_seats)  # Update room status with exact zone name

        elif room_name.startswith('A') or room_name.startswith('C'):
            room_stat_df = read_room_status(room_name=room_name)
            if room_stat_df is not None:
                filled_seats = room_stat_df.loc[room_stat_df['Room Name']==room_name,"Filled Seats"].values[0]
    
            # Regular room (C, A, etc.) with sequential seating
            for seat_number in range(filled_seats+1, assigned_capacity+filled_seats+1):
                if student_index >= len(course_students):
                    break

                student = course_students.iloc[student_index]
                seat_allocation.append({
                    'System ID' : student['ID'],
                    'Email':student['Email'],
                    'Student Name': student['Name'],
                    'Student ID': student['Campus ID'],
                    'Course': student['Subject_Catalog'],
                    'Room': room_name,
                    'Seat Number': seat_number
                })
                student_index += 1
                update_room_csv(room_name=room_name,capacity=assigned_capacity,filled_seats=filled_seats+seat_number)
        

    # Create a DataFrame from the seating allocation
    seat_allocation_df = pd.DataFrame(seat_allocation)
    # Display the final seat allocation DataFrame
    return seat_allocation_df


def update_room_csv(room_name=None, capacity=0, filled_seats=0, limit_type=" ", filepath="data\\room_status.csv"):
    """Update room status CSV. Initialize with headers if it doesn't exist; otherwise, update or add room info."""
    
    # Check if the CSV file exists
    if not os.path.exists(filepath):
        # Create an empty CSV with headers only if the file doesn't exist
        room_status_df = pd.DataFrame(columns=['Room Name', 'Capacity', 'Filled Seats', 'Limit Type'])
        room_status_df.to_csv(filepath, index=False)
    
    # Load existing data
    room_status_df = pd.read_csv(filepath)

    # If room info is provided, update/add the room entry
    if room_name and capacity!= 0 and filled_seats!= 0:
        # Check if the room already exists in the CSV
        if room_name in room_status_df['Room Name'].values:
            # Update the filled seats and capacity for the existing room
            room_status_df.loc[room_status_df['Room Name'] == room_name, ['Capacity', 'Filled Seats', 'Limit Type']] = [capacity, filled_seats, limit_type]
        else:
            # Add a new row for the new room
            new_room = pd.DataFrame([[room_name, capacity, filled_seats, limit_type]], columns=['Room Name', 'Capacity', 'Filled Seats', 'Limit Type'])
            room_status_df = pd.concat([room_status_df, new_room], ignore_index=True)

        # Save the updated DataFrame back to the CSV
        room_status_df.to_csv(filepath, index=False)




def read_room_status(filepath="data\\room_status.csv", room_name=None):
    """Read the room status CSV and return the DataFrame or specific room details."""
    
    # Check if the CSV file exists
    try:
        room_status_df = pd.read_csv(filepath)
        
        # If a room name is specified, filter the DataFrame
        if room_name is not None:
            specific_room = room_status_df[room_status_df['Room Name'] == room_name]
            if not specific_room.empty:
                return specific_room
            else:
                #print(f"Room '{room_name}' not found in the room status.")
                return None
        else:
            return None
    except FileNotFoundError:
        print(f"File {filepath} not found. Please initialize the room status CSV.")
        
        return pd.DataFrame(columns=['Room Name', 'Capacity', 'Filled Seats', 'Limit Type'])  # Return an empty DataFrame with headers if file doesn't exist
