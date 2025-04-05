from shared import *
from allocate_ops import *
from shared import errors_dict, LT_names, DLT_names, CC_lab,course_count

def allocate_rooms(rooms, students, course_name,date,time):
    """ Function to allocate room and seat number to students for the given course. """
    equivalent_course = False #Flag to help in future
    #For courses like EEE F244/ ECE F244/ INSTR F244
    #print(course_name)
    #course_name = re.sub(r'\s+', ' ', course_name) #combatting any non-breaking spaces (\xa0)
    related_courses = [course.strip() for course in course_name.split('/ ')]
    print(related_courses)
    if(len(related_courses)>1):
        equivalent_course = True

    course_students = students[students['Subject_Catalog'].isin(related_courses)]
    course_count = len(course_students)
    print("LENGTH OF COURSE",len(course_students))
    if course_students.empty:
        print("No students found for the exact course or related courses.")

    course_rooms = rooms[rooms['Course'] == course_name]
    #print("COURSE ROOMS:", course_rooms)
    seat_allocation = []

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

        #classes_df = pd.read_excel(r"data\room_data\Classrooms.xlsx", skiprows=1, header=None, names=['Room Name', 'Capacity'])
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
            # print("Full Capacity of Room:", aggregated_capacity_room)
            # print("aggregated capacity:", aggregated_capacity_room)

            room_stat_df = read_room_status(room_name=room_name)

            if room_stat_df is not None:
                filled_seats = room_stat_df.loc[room_stat_df['Room Name']==room_name,"Filled Seats"].values[0]
    
            # print(dlt_seats)
            for seat_number in range(filled_seats+1, len(dlt_seats)+1):
                if(count_seats>=assigned_capacity):
                    update_room_csv(room_name=room_name, capacity= aggregated_capacity_room,filled_seats=seat_number-1,limit_type=" ")
                    count_seats=0
                    break
                elif ((student_index >= len(course_students))|(seat_number>aggregated_capacity_room)):
                    update_room_csv(room_name=room_name, capacity= aggregated_capacity_room,filled_seats=seat_number-1,limit_type=" ")
                    count_seats=0
                    break
                actual_seat = dlt_seats.get(seat_number, seat_number)
                #print("STUDENT INDEX",student_index,"filled seats ",filled_seats,"seat num ", seat_number)
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
            #cc_filepath = "data\\room_data\\CCLab_HardLimit.xlsx" if cc_total_capacity > 202 else "data\\room_data\\CCLab_SoftLimit.xlsx"
            cc_seat_mapping = load_cc_seating_arrangement(find_cc_hard_soft(course_name))
            #cc_seat_mapping = load_cc_seating_arrangement(cc_filepath)

            #number of filled seats from room_status.csv
            # Handle CC rooms using specific zones and seating arrangement
            zone_keys = CC_lab[room_name]  # Get zone(s) associated with this CC room
            #print("zone keys",zone_keys)
            #print("hello", cc_seat_mapping)
            if isinstance(zone_keys, list):
                capacity_for_zone_3 = len(cc_seat_mapping.get( "CC LAB-ZONE 3A", []))+len(cc_seat_mapping.get( "CC LAB-ZONE 3B", []))
                capacity_for_zone_3A = len(cc_seat_mapping.get( "CC LAB-ZONE 3A", []))
                capacity_for_zone_3B = len(cc_seat_mapping.get( "CC LAB-ZONE 3B",[]))

                print("Capacities:",capacity_for_zone_3,capacity_for_zone_3A, capacity_for_zone_3B)
                # Process for rooms with multiple zones (e.g., CCz3 with "CC LAB-ZONE 3A" and "CC LAB-ZONE 3B")
                for zone in zone_keys:
                    # Strip the last alphabet from the zone name
                    
                    stripped_zone = zone[:-1] if zone[-1].isalpha() else zone
                    #print("zone: ",zone)
                    room_stat_df = read_room_status(room_name=stripped_zone) #CHECK THIS COZ NEED TO SEE AGGREGATE CAPACITY OF ZONE 3
                    room_df = read_room_status(room_name=zone)
                    
                    if room_stat_df is not None:
                        filled_seats = room_stat_df.loc[room_stat_df['Room Name']==stripped_zone,"Filled Seats"].values[0]
                        #print("filled",filled_seats)
                    else:
                        filled_seats = 0

                    if room_df is not None:
                        zone_filled_seats = room_df.loc[room_df['Room Name']==zone,"Filled Seats"].values[0] 
                        print("zone filled",zone_filled_seats)
                    else:
                        zone_filled_seats = 0
                    
                    seat_numbers = cc_seat_mapping.get(zone, [])
                    capacity_for_zone=len(seat_numbers)

                    print("ZONE FILLED AND CAPACITY",zone_filled_seats, capacity_for_zone)
                    if((zone == "CC LAB ZONE 3A") & (zone_filled_seats>=capacity_for_zone)):
                        print("ZONE FILLED SEATS BREAKING HERE ",zone_filled_seats)
                        continue

                    if((zone == "CC LAB-ZONE 3A") & (zone_filled_seats == 0)):
                        room_stat_df = read_room_status(room_name=zone)
                        #print(student_index)
                        if room_stat_df is not None:
                            #print(room_stat_df['Room Name']==zone)
                            filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone,"Filled Seats"].values[0]
                        else:
                            filled_seats = 0
                            print(f"REACHED FOR {room_name} ")
                        print("CURRENT IF 1")
                        print("ZONE FILLED SEATS",zone_filled_seats)
                        for seat_number in range(zone_filled_seats,len(seat_numbers)):
                        #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity,"seat number:",seat_number)
                            if seat_number >= capacity_for_zone:
                                print(f"REACHED1 FOR {room_name} ")
                                break
                            
                            elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                                # print(len(course_students))
                                print("ZONE FILLED SEATS",zone_filled_seats)
                                print(cc_total_capacity)
                                print(f"REACHED2 FOR {room_name} ")
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

                        update_room_csv(room_name=stripped_zone, capacity=capacity_for_zone_3, filled_seats=filled_seats)  # Update room status with exact zone name
                        update_room_csv(room_name=zone, capacity=capacity_for_zone, filled_seats=filled_seats)

                    if((zone == "CC LAB-ZONE 3A") & (zone_filled_seats != 0)&(zone_filled_seats<=capacity_for_zone)):
                        room_stat_df = read_room_status(room_name=zone)
                        #print(student_index)
                        if room_stat_df is not None:
                            #print(room_stat_df['Room Name']==zone)
                            filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone,"Filled Seats"].values[0]
                        else:
                            filled_seats = 0
                            print(f"REACHED FOR {room_name} ")
                        print("CURRENT IF 2")
                        print("ZONE FILLED SEATS",zone_filled_seats)
                        for seat_number in range(zone_filled_seats,len(seat_numbers)):
                        #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity,"seat number:",seat_number)
                            if seat_number >= capacity_for_zone:
                                print(f"REACHED1 FOR {room_name} ")
                                break
                            
                            elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                                # print(len(course_students))
                                print("ZONE FILLED SEATS",zone_filled_seats)

                                print(cc_total_capacity)
                                print(f"REACHED2 FOR {room_name} ")
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

                        update_room_csv(room_name=stripped_zone, capacity=capacity_for_zone_3, filled_seats=filled_seats)  # Update room status with exact zone name
                        update_room_csv(room_name=zone, capacity=capacity_for_zone, filled_seats=filled_seats)

                    if((zone == "CC LAB-ZONE 3B") & (zone_filled_seats == 0)):
                        print("CURRENT IF 3")
                        print("ZONE FILLED SEATS",zone_filled_seats)
                        room_stat_df = read_room_status(room_name=zone)
                        #print(student_index)
                        if room_stat_df is not None:
                            #print(room_stat_df['Room Name']==zone)
                            filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone,"Filled Seats"].values[0]
                        else:
                            filled_seats = 0
                            print(f"REACHED FOR {room_name} ")
                        for seat_number in range(zone_filled_seats,len(seat_numbers)):
                        #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity,"seat number:",seat_number)
                            if seat_number >= capacity_for_zone:
                                print(f"REACHED1 FOR {room_name} ")
                                break
                            
                            elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                                # print(len(course_students))
                                print("ZONE FILLED SEATS",zone_filled_seats)
                                print(f"REACHED2 FOR {room_name} ")
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

                        update_room_csv(room_name=stripped_zone, capacity=capacity_for_zone_3, filled_seats=filled_seats)  # Update room status with exact zone name
                        update_room_csv(room_name=zone, capacity=capacity_for_zone, filled_seats=filled_seats)

                        
                    if((zone == "CC LAB-ZONE 3B") & (zone_filled_seats != 0)):
                        print("CURRENT IF 4")
                        print("ZONE FILLED SEATS",zone_filled_seats)
                        room_stat_df = read_room_status(room_name=zone)
                        #print(student_index)
                        if room_stat_df is not None:
                            #print(room_stat_df['Room Name']==zone)
                            filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone,"Filled Seats"].values[0]
                        else:
                            filled_seats = 0
                            print(f"REACHED FOR {room_name} ")
                        for seat_number in range(zone_filled_seats,len(seat_numbers)):
                        #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity,"seat number:",seat_number)

                            if seat_number >= capacity_for_zone:
                                print(f"REACHED1 FOR {room_name} ")
                                break
                            
                            elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                                # print(len(course_students))
                                print("ZONE FILLED SEATS",zone_filled_seats)
                                print(f"REACHED2 FOR {room_name} ")
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

                        update_room_csv(room_name=stripped_zone, capacity=capacity_for_zone_3, filled_seats=filled_seats)  # Update room status with exact zone name
                        update_room_csv(room_name=zone, capacity=capacity_for_zone, filled_seats=filled_seats)

                    print("MAPPING",seat_numbers)

                    # if(zone == "CC LAB-ZONE 3B"): 
                    #     room_stat_df = read_room_status(room_name=zone)
                    #     #print(student_index)
                    #     if room_stat_df is not None:
                    #         #print(room_stat_df['Room Name']==zone)
                    #         filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone,"Filled Seats"].values[0]
                    #     else:
                    #         filled_seats = 0
                    #         print(f"REACHED FOR {room_name} ")
                    
                    # for seat_number in range(filled_seats,len(seat_numbers)):
                    #     #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity,"seat number:",seat_number)
                    #     if seat_number >= capacity_for_zone:
                    #         print(f"REACHED1 FOR {room_name} ")
                    #         break
                        
                    #     elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                    #         # print(len(course_students))
                    #         print(filled_seats)
                    #         print(cc_total_capacity)
                    #         print(f"REACHED2 FOR {room_name} ")
                    #         break
                    #     student = course_students.iloc[student_index]
                    #     seat_allocation.append({
                    #         'System ID' : student['ID'],
                    #         'Email':student['Email'],
                    #         'Student Name': student['Name'],
                    #         'Student ID': student['Campus ID'],
                    #         'Course': student['Subject_Catalog'],
                    #         'Room': zone,  # Updated room name to reflect the exact zone
                    #         'Seat Number': seat_numbers[seat_number]
                    #     })
                    
                    #     student_index += 1
                    #     filled_seats += 1

                    # update_room_csv(room_name=stripped_zone, capacity=capacity_for_zone_3, filled_seats=filled_seats)  # Update room status with exact zone name
                    # update_room_csv(room_name=zone, capacity=capacity_for_zone, filled_seats=filled_seats)
            else:
                # Process for rooms with a single zone (e.g., CCz1 or CCz2)
                #print("WE WENT TO ELSE STATEMENT! CC")
                
                seat_numbers = cc_seat_mapping.get(zone_keys)
                capacity_for_zone=len(seat_numbers)
                room_stat_df = read_room_status(room_name=zone_keys)
                if room_stat_df is not None:
                        filled_seats = room_stat_df.loc[room_stat_df['Room Name']==zone_keys,"Filled Seats"].values[0]
                        #print("filled IN ELSE",filled_seats)
                
                #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity)
                count_seats=0
                for seat_number in range(filled_seats,len(seat_numbers)):
                    #print("studentindex:",student_index,"ASSIGNED:",assigned_capacity,"seat number:",seat_number)
                    
                    if seat_number >= capacity_for_zone or count_seats>=assigned_capacity:
                        #print(f"REACHED1 FOR  {room_name}")
                        break
                    elif student_index >= len(course_students) or filled_seats >= cc_total_capacity:
                        #print(f"REACHED2 FOR  {room_name}")
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
                    count_seats+=1
                    filled_seats += 1
                update_room_csv(room_name=zone_keys, capacity=capacity_for_zone, filled_seats=filled_seats)  # Update room status with exact zone name

        elif room_name.startswith('A') or room_name.startswith('C'):
            room_stat_df = read_room_status(room_name=room_name)
            #print("ROOM STATUS A/C", room_stat_df)
            #print(assigned_capacity)
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