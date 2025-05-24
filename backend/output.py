#generate output PDFs: 3 kinds for now & Output Excel Sheet for Mastersheet 
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table as PlatypusTable
from reportlab.lib.units import inch
from PyPDF2 import PdfMerger #combine PDFs
from output_ops import * 
from shared import errors_dict, os, datetime, pd

#IC PDF
def create_pdf(df, time_slot, date, IC_name, Course_title, course_num, regdata, course_count, IC_file_path, exam_title="COMPREHENSIVE EXAMINATION SEMESTER I 24-25"):
    # Create the PDF document
    if not os.path.exists("Output\\Student Seating"):
        os.makedirs("Output\\Student Seating")
    
    if not os.path.exists("Output\\IC"):
        os.makedirs("Output\\IC")
    
    if not os.path.exists("Output\\Combined_Seating"):
        os.makedirs("Output\\Combined_Seating")

    elements = []

    try:
        # Extract the date part only (before the comma)
        date_part = date.split(',')[0].strip()
        # Convert to a datetime object
        date_obj = datetime.strptime(date_part, "%d/%m/%Y")
        # Format as folder-friendly name (e.g., "2024-05-08")
        folder_name = date_obj.strftime("%d-%m-%Y")
    except ValueError as e:
        print("Invalid date format. Please provide a date in 'DD/MM/YYYY, Day' format.")
        if course_num in errors_dict:
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            errors_dict[course_num].append(f"output.py: Value Error & {e}")
        else:
            errors_dict[course_num] = e
        return

    

    student_count = len(df)
    styles = getSampleStyleSheet()
    
    # Create a custom style for the exam title
    exam_style = styles['Title']
    exam_style.alignment = 1  # Center alignment
    exam_style.textColor = colors.HexColor('#8B0000')  # Maroon color
    exam_style.fontSize = 25
    exam_style.spaceAfter = 15
    
    # Add exam title with maroon highlight 
    elements.append(Paragraph(f"<b>{exam_title}</b>", exam_style))
    
    # Create a table for the course info with dynamic width
    info_data = [
        [Paragraph(f"<b>Course No. & Title:</b> {course_num} {Course_title}", styles['Normal'])],
        [
            Paragraph(f"<b>Date:</b> {date}", styles['Normal']),
            Paragraph(f"<b>Time:</b> {time_slot}", styles['Normal'])
        ],
        [Paragraph(f"<b>IC:</b> {IC_name}", styles['Normal'])],
        [Paragraph(f"<b>Total Students:</b> {student_count}", styles['Normal'])]
    ]
    
    # Calculate available width (leaving margins)
    available_width = letter[0] - 40
    
    # Create a table for each row to handle dynamic content
    for i, row in enumerate(info_data):
        if i == 1:  # For date and time row
            col_widths = [available_width * 0.5, available_width * 0.5]
            row_table = Table([row], colWidths=col_widths)
        else:
            row_table = Table([[row[0]]], colWidths=[available_width])
        
        # Style each row with consistent borders
        row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),  # Light gray background
        ]))
        
        elements.append(row_table)
    
    # Add some space before the main table
    elements.append(Spacer(1, 20))
    
    try:
        course_name = df['Course'][0]  # Assuming the course name is in the 'Course' column
    except Exception as e: 
        print(f"An error occurred in creating pdf: {e} for {course_num} {Course_title}")
        if course_num in errors_dict:
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            errors_dict[course_num].append(f"output.py: Create PDF & {e}")
        else:
            errors_dict[course_num] = e
        return 0

    # Create date-based directory structure
    # Base path for date folders
    
    

    # Prepare the seating table
    df = df.drop(columns=['Course'])
    pdf_df = df.copy()
    pdf_df = pdf_df.drop(columns=['Email', 'System ID'])
    pdf_df.insert(0, 'S.No', range(1, len(df) + 1))  # Serial number starts from 1
    pdf_df = pdf_df[['S.No', 'Student ID', 'Student Name','Room','Seat Number']]  # Reorder columns
    
    # Convert data to list of lists
    data = [pdf_df.columns.tolist()] + pdf_df.values.tolist()
    
    # Calculate column widths
    col_widths = [
        0.7 * inch,  # S.No
        1.5 * inch,  # Student ID
        3.0 * inch,  # Student Name (increased width)
        1.2 * inch,  # Seat Number
        1.5 * inch   # Room
    ]
    
    # Create the table with specified column widths
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Define table style
    style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2f0d9')),  # Dark green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),          # White text
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                      # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),            # Bold header font
        ('FONTSIZE', (0, 0), (-1, 0), 12),                          # Header font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),                      # Header padding
        ('TOPPADDING', (0, 0), (-1, 0), 4),                         # Header top padding
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),               # Grid lines
        ('BOX', (0, 0), (-1, -1), 1, colors.black),                  # Outer border
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        bg_color = colors.beige if i % 2 == 0 else colors.white
        #bg_color = colors.HexColor('#D9E1F2') if i % 2 == 0 else colors.white  # Light blue and white
        style.add('BACKGROUND', (0, i), (-1, i), bg_color)
    
    # Apply the style to the table
    table.setStyle(style)

    # Add table to the PDF
    elements.append(table)

    # Rearrange output DataFrame columns as per requirement
    output_df = df
    output_df['Course Title'] = Course_title
    output_df['Time'] = time_slot
    output_df['IC'] = IC_name
    output_df['Date'] = date
    output_df['Course'] = course_num
    
    # Reorder columns
    output_df = output_df[['Student ID', 'System ID', 'Student Name','Course', 'Course Title', 'Date', 'Time', 'Email','IC', 'Room', 'Seat Number']]

    related_courses = [course.strip() for course in str(course_name).split('/')]

    for i, row in output_df.iterrows():
        # Extract possible related courses from the current row
        related_courses = [course.strip() for course in row['Course'].split('/ ')]
        
        # Find the matching row in regdata based on Student ID and related courses
        matched_row = regdata[
            (regdata['Campus ID'] == row['Student ID']) &
            (regdata['Subject_Catalog'].isin(related_courses))
        ]
        
        if not matched_row.empty:
            # Update the 'Course' column in output_df with the matched Subject_Catalog
            output_df.at[i, 'Course'] = matched_row.iloc[0]['Subject_Catalog']

    #excel sheet
    file_path = "Output\\output_file.xlsx"
    create_output_excel(output_df,file_path,IC_file_path)

    course_name=clean_filename(course_name)
    date_str = date.replace('/', '-')
    output_dir = os.path.join("Output", "IC", date_str)
    # Create the PDF document with proper margins
    output_path = os.path.join(output_dir, f"{course_name}.pdf")
    os.makedirs(output_dir, exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Build the PDF document with all elements (table is already included in elements)
    doc.build(elements)
    
    # Check student count
    if student_count != course_count:
        error_msg = f"Total count of students for course & count of allocations doesn't match for: {course_num}, should be {course_count} is {student_count}"
        print(error_msg)
        
        if course_num in errors_dict:
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            # Append the new error to the list
            errors_dict[course_num].append(f"Count doesn't match")
        else:
            # If course doesn't exist, create a new key-value pair
            if course_num in errors_dict:
            # If the value is not already a list, convert it to a list
                if not isinstance(errors_dict[course_num], list):
                    errors_dict[course_num] = [errors_dict[course_num]]
            # Append the new error to the list
                errors_dict[course_num].append(f"Count doesn't match should be {course_count} is {student_count}")
            else:
            # If course doesn't exist, create a new key-value pair
                errors_dict[course_num] = f"COUNT NOT MATCHING should be {course_count} is {student_count}"

    print(f"*****Created the IC pdf for {course_name}!*****")


#OUTPUT EXCEL
def create_output_excel(output_df,file_path="Output\\output_file.xlsx",IC_file_path = "data\\ICS.xlsx"):
    # Create a new output Excel file
    print("****CREATING EXCEL NOW!****")

    ic_df = pd.read_excel(IC_file_path, skiprows=0, header=0) #change this when interface
    if 'Subject_Catalog' not in ic_df.columns:
        # Add the 'Subject_Catalog' column
        if all(col in ic_df.columns for col in ['Subject', 'Catalog']):
            ic_df['Subject_Catalog'] = ic_df['Subject'].str.strip() + ' ' + ic_df['Catalog'].str.strip()
            #print("'Subject_Catalog' column added successfully.")

            with pd.ExcelWriter(IC_file_path, engine="openpyxl", mode="w") as writer:
                ic_df.to_excel(writer, index=False, sheet_name="IC")
            #print(f"Updated Excel file saved to {IC_file_path}.")

        else:
            print("Required columns 'Subject' and 'Catalog' not found in the Excel file.")
            return
    else:
        #print("'Subject_Catalog' column already exists. No changes made.")
        pass

    ic_df = pd.read_excel(IC_file_path, skiprows=0, header=0)

    """Stop getting SettingWithCopyWarning warning; fix this later"""
    pd.set_option('mode.chained_assignment', None) 

    # Loop through output DataFrame and update Instructor ID based on Subject_Catalog match
    for index, row in output_df.iterrows():
        matched_row = ic_df[ic_df['Subject_Catalog'] == row['Course']]
        if not matched_row.empty:
            output_df.loc[index:, 'PSRN'] = matched_row['PSRN'].values[0]
        else:
            output_df.loc[index, 'PSRN'] = None


    output_df = output_df[['Student ID', 'System ID', 'Student Name','Course', 'Course Title', 'Date', 'Time', 'Email','IC', 'PSRN','Room', 'Seat Number']]
    if not os.path.exists(file_path):
        output_df.to_excel(file_path, index=False, sheet_name="Sheet1")
    else:
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            output_df.to_excel(writer, sheet_name="Sheet1", index=False, header=False, startrow=writer.sheets["Sheet1"].max_row)



def generate_room_pdfs(seat_allocation_df, time_slot, date, IC_name, Course_title,course_num,course_count,exam_title):
    """ Generate a PDF for each room's seating arrangement. """
    print("****ENTERED GENERATING ROOM PDFS****")
    try:
        rooms = seat_allocation_df['Room'].unique()
        individual_pdfs = []  

        for room in rooms:
            room_data = seat_allocation_df[seat_allocation_df['Room'] == room]
            pdf_path = create_attendance_pdfs(room, room_data, time_slot, date, IC_name, Course_title,course_num,exam_title)
            individual_pdfs.append(pdf_path)
        course_num = clean_filename(course_num)
        combined_pdf_path = os.path.join(
            "Output",
            "Combined_Seating",
            f"{course_num}_Combined_Seating_Plan.pdf"
        )
        combine_pdfs(individual_pdfs, combined_pdf_path)
        print(f"****Created combined PDF: {combined_pdf_path}****")

    except Exception as e:
        print(f"An error occurred: {e} for course {course_num}")
        #errors dict, optimize this:
        if course_num in errors_dict:
            # If the value is not already a list, convert it to a list
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            # Append the new error to the list
            errors_dict[course_num].append(f"output.py: Generate Room PDFs & {e}")
        else:
            # If course doesn't exist, create a new key-value pair
            errors_dict[course_num] = e
        return 0


def create_attendance_pdfs(room_num, df, time_slot, date, IC_name, Course_title, course_num, exam_title="COMPREHENSIVE EXAMINATION SEMESTER I 24-25"):
    """ Create a PDF for a single room with signature boxes and updated header format. """
    course_name = df['Course'].values[0] if 'Course' in df.columns else 'N/A'
    elements = []
    styles = getSampleStyleSheet()
    
    # Create a custom style for the exam title
    exam_style = styles['Title']
    exam_style.alignment = 1  # Center alignment
    exam_style.textColor = colors.HexColor('#8B0000')  # Maroon color
    exam_style.fontSize = 25
    exam_style.spaceAfter = 15
    
    # Add exam title with maroon highlight
    elements.append(Paragraph(f"<b>{exam_title}</b>", exam_style))
    
    # Get room name and student count
    room_name = df['Room'].values[0] if 'Room' in df.columns else 'N/A'
    student_count = len(df)
    
    # Create a table for the course info with dynamic width
    info_data = [
        [Paragraph(f"<b>Course No. & Title:</b> {course_num} {Course_title}", styles['Normal'])],
        [
            Paragraph(f"<b>Date:</b> {date}", styles['Normal']),
            Paragraph(f"<b>Time:</b> {time_slot}", styles['Normal'])
        ],
        [Paragraph(f"<b>Room:</b> {room_name}", styles['Normal'])],
        [Paragraph(f"<b>IC:</b> {IC_name}", styles['Normal'])],
        [Paragraph(f"<b>Total Students:</b> {student_count}", styles['Normal'])]
    ]
    
    # Calculate available width (leaving margins)
    available_width = letter[0] - 40
    
    # Create a table for each row to handle dynamic content
    for i, row in enumerate(info_data):
        if i == 1:  # For date and time row
            col_widths = [available_width * 0.5, available_width * 0.5]
            row_table = Table([row], colWidths=col_widths)
        else:
            row_table = Table([[row[0]]], colWidths=[available_width])
        
        # Style each row with consistent borders
        row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),  # Light gray background
        ]))
        
        elements.append(row_table)
    
    # Add some space before the main table
    elements.append(Spacer(1, 20))

    # Drop columns not needed in the seating table
    df = df.drop(columns=['Course'])
    df.insert(0, 'Serial No', range(1, len(df) + 1))  # Serial number starts from 1
    
    pdf_df = df.copy()
    pdf_df = pdf_df.drop(columns=['Email', 'System ID'])

    pdf_df = pdf_df[['Serial No','Student ID','Student Name','Room','Seat Number']] #reordering so ID in front, change later: optimize
    
    # Add a "Signature" column for student signatures
    pdf_df['Signature'] = ''  # Empty column for signature

    # Convert the DataFrame to a list of lists for the ReportLab Table
    data = [pdf_df.columns.tolist()] + pdf_df.values.tolist()

    # Define column widths (adjust as needed)
    col_widths = [
        0.7 * inch,  # Serial No
        1.2 * inch,  # Student ID
        2.5 * inch,  # Student Name
        1.5 * inch,  # Room
        1.0 * inch,  # Seat Number
        1.0 * inch   # Signature
    ]
    
    # Create the seating table with specified column widths
    table = Table(data, colWidths=col_widths, repeatRows=1)

    
    # Define table style
    style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2f0d9')),  # Dark blue header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),          # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                      # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),            # Header font
        ('FONTSIZE', (0, 0), (-1, -1), 12),                         # Font size for all cells
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),                     # Header bottom padding
        ('TOPPADDING', (0, 0), (-1, -1), 4),                        # Top padding for all cells
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),                     # Bottom padding for all cells
        ('LEFTPADDING', (0, 0), (-1, -1), 4),                       # Left padding for all cells
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),                      # Right padding for all cells
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),              # Grid lines
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        bg_color = colors.beige if i % 2 == 0 else colors.white
        style.add('BACKGROUND', (0, i), (-1, i), bg_color)
    
    # Apply the style to the table
    table.setStyle(style)


    course_name=clean_filename(course_name)
    #Output folder path
    folder_name = clean_name(IC_name.strip()) #Use something better, PSRN or Email ID Name

    # Base path for date folders
    base_path = "Output//Student Seating//"
    full_path = os.path.join(base_path, folder_name)

    # Ensure the date folder exists
    os.makedirs(full_path, exist_ok=True)
    try:
        
        output_path = os.path.join(full_path, f"{course_name}_Seating_Plan_{room_num}.pdf")
        #output_path = os.path.join(full_path, f"{course_name}_Seating_Plan_{room_num}.pdf")
        pdf = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    except Exception as e:
        # Handle the error and fallback to a default path
        print(f"Error occurred while creating the PDF at the specified path: {e}")
        

        output_path = f"Output\\Student Seating\\{course_name}_Seating_Plan_{room_num}.pdf"
        pdf = SimpleDocTemplate(output_path, pagesize=letter)

    # Add the table to the PDF
    elements.append(table)

    # Build the PDF
    pdf.build(elements)
    print(f"Created {course_num} PDF for room: {room_name}!")
    return output_path

#COMBINED SEATING PDF
def combine_pdfs(pdf_paths, output_path):
    """ Combine multiple PDFs into a single PDF with each starting on a new page. """
    merger = PdfMerger()

    for pdf in pdf_paths:
        if pdf:  # Ensure the path is valid
            merger.append(pdf)

    # Write the combined PDF
    with open(output_path, "wb") as output_file:
        merger.write(output_file)
        merger.close()

