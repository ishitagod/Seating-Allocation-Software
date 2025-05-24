from shared import *

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


def find_cc_hard_soft(course_name,input_file_path="data/input-file-rooms.xlsx"):
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
    
    df = aggregated_capacity[
    (aggregated_capacity['Room'].str.startswith('CC')) & 
    (aggregated_capacity['Date'] == date) & 
    (aggregated_capacity['Time'] == time_slot)
    ][['Room', 'Capacity']].reset_index(drop=True)
        # Calculate CC total capacity for the specified Date and Time
    #print(df) 

    #print("CC total capacity for time and day: ",cc_total_capacity)

    cc_filepath_hard= "data\\room_data\\CCLab_HardLimit.xlsx" 
    cc_filepath_soft="data\\room_data\\CCLab_SoftLimit.xlsx"
    
    cc_soft_seats = load_cc_seating_arrangement(cc_filepath_soft)
    cc_hard_seats = load_cc_seating_arrangement(cc_filepath_hard)

    for _, row in df.iterrows():
        room_name = row['Room']
        room_capacity = row['Capacity']

        if room_name in CC_lab:
            zone_keys = CC_lab[room_name]  # Get zone(s) associated with this CC room
            
            if isinstance(zone_keys, list):  # If multiple zones (e.g., CCz3)
                total_soft_capacity = sum(len(cc_soft_seats.get(zone, [])) for zone in zone_keys)
                print(total_soft_capacity)
                #total_hard_capacity = sum(len(cc_hard_seats.get(zone, [])) for zone in zone_keys)

                if room_capacity > total_soft_capacity:
                    print(f"⚠️  {zone_keys} exceed soft limit! Using Hard Limit file.")
                    return cc_filepath_hard
            else:  # If a single zone (e.g., "CCz1")
                soft_capacity = len(cc_soft_seats.get(zone_keys, []))
                hard_capacity = len(cc_hard_seats.get(zone_keys, []))

                if room_capacity > soft_capacity:
                    print(f"⚠️  {zone_keys} exceeds soft limit! Using Hard Limit file.")
                    return cc_filepath_hard
    
    return cc_filepath_soft
    
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
