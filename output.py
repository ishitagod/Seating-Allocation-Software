#generate output PDFs: 3 kinds for now & Output Excel Sheet for Mastersheet 
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table as PlatypusTable
from reportlab.lib.units import inch
import os
from datetime import datetime
import pandas as pd
from PyPDF2 import PdfMerger #combine PDFs
from data_ops import * 
from shared import errors_dict

def create_pdf(df,time_slot, date, IC_name, Course_title, course_num, regdata, exam_title="COMPREHENSIVE EXAMINATION SEMESTER I 24-25"):
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
    except ValueError:
        print("Invalid date format. Please provide a date in 'DD/MM/YYYY, Day' format.")
        if course_num in errors_dict:
            # If the value is not already a list, convert it to a list
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            # Append the new error to the list
            errors_dict[course_num].append(f"output.py: Value Error & {e}")
        else:
            # If course doesn't exist, create a new key-value pair
            errors_dict[course_num] = e
        return

    # Base path for date folders
    base_path = "Output/IC/"
    full_path = os.path.join(base_path, folder_name)

    # Ensure the date folder exists
    os.makedirs(full_path, exist_ok=True)
    #print(df.head())

    # Add a header image
    header_image_path = "data\\bits_logo.jpeg"
    header_image = Image(header_image_path, 1.5*inch, 1.5*inch)

    # Add a text header
    styles = getSampleStyleSheet()
    header = Paragraph(exam_title, styles['Title'])  #Header text
    header_data = [
        [Paragraph(f"<b>Course No & Title:</b> {Course_title}", styles['Normal'])],
        [Paragraph(f"<b>Date:</b> {date}", styles['Normal']),
         Paragraph(f"<b>Time:</b> {time_slot}", styles['Normal']), 
         Paragraph(f"<b>IC: {IC_name}</b>", styles['Normal'])]
    ]
    try:
        course_name = df['Course'][0] # Assuming the course name is in the 'Course' column
    except Exception as e: 
        print(f"An error occurred in creating pdf: {e} for {course_num} {Course_title}")
        if course_num in errors_dict:
            # If the value is not already a list, convert it to a list
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            # Append the new error to the list
            errors_dict[course_num].append(f"output.py: Create PDF & {e}")
        else:
            # If course doesn't exist, create a new key-value pair
            errors_dict[course_num] = e
        return 0
    
    header_table = Table(header_data, colWidths=[4 * inch, 4 * inch])  # Full width
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Align the text vertically with the image
    ]))
    
    # Build the PDF
    # pdf.build(elements)
    elements.append(header_table)

    # Add some space after the header
    elements.append(Spacer(1, 12))

    # Convert the DataFrame to a list of lists for the ReportLab Table
    df = df.drop(columns=['Course'])
    pdf_df = df 
    pdf_df = pdf_df.drop(columns=['Email', 'System ID'])
    pdf_df.insert(0, 'Serial No', range(1, len(df) + 1))  # Serial number starts from 1
    pdf_df = pdf_df[['Serial No', 'Student ID', 'Student Name','Room','Seat Number']]#reordering so ID in front, change later: optimize
    data = [pdf_df.columns.tolist()] + pdf_df.values.tolist()
    
    # Create the table
    table = Table(data)

    # Add table styling
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),          # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),     # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),                   # Align text to left
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),       # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),                # Padding for the header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),        # Background color for other rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),           # Adding grid lines to make table lines prominent
    ])
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
    #print(output_df.head())
    
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
    create_output_excel(output_df,file_path)

    # Build the PDF
    
    course_name=clean_filename(course_name)
    pdf_path = os.path.join(full_path, f"{course_name}.pdf")
    
    #output_path = f"Output\\IC\\{course_name}.pdf"
    #pdf = SimpleDocTemplate(output_path, pagesize=letter)
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    # Build the PDF
    pdf.build(elements)
    print(f"*****Created the IC pdf for {course_name}!*****")


def create_output_excel(output_df,file_path="Output\\output_file.xlsx"):
    # Create a new output Excel file
    print("****CREATING EXCEL NOW!****")
    IC_file_path = "data\\ICS.xlsx"

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
            output_df.loc[index:, 'Instructor ID'] = matched_row['Instructor ID'].values[0]
        else:
            output_df.loc[index, 'Instructor ID'] = None


    output_df = output_df[['Student ID', 'System ID', 'Student Name','Course', 'Course Title', 'Date', 'Time', 'Email','IC', 'Instructor ID','Room', 'Seat Number']]
    if not os.path.exists(file_path):
        output_df.to_excel(file_path, index=False, sheet_name="Sheet1")
    else:
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            output_df.to_excel(writer, sheet_name="Sheet1", index=False, header=False, startrow=writer.sheets["Sheet1"].max_row)



def generate_room_pdfs(seat_allocation_df, time_slot, date, IC_name, Course_title,course_num,exam_title):
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
    course_name = df['Course'].values[0]
    elements = []



    # Header styling and content
    styles = getSampleStyleSheet()
    exam_header = Paragraph(exam_title, styles['Title'])
    elements.append(exam_header)

    course_name = df['Course'].values[0] if 'Course' in df.columns else 'N/A'
    course_name=clean_filename(course_name)
    room_name = df['Room'].values[0]
      # Assuming instructor name is constant for this example
    student_count = len(df)
    # Create header table content
    header_data = [
        [Paragraph(f"<font color='red'><b>Course:</b></font> {course_num} {Course_title}", styles['Normal'])],
        [Paragraph(f"<font color='red'><b>Room:</b></font> {room_num}", styles['Normal'])],
        [Paragraph(f"<font color='red'><b>Date:</b></font> {date}", styles['Normal']),
         Paragraph(f"<font color='red'><b>Time:</b></font> {time_slot}", styles['Normal'])],
        [Paragraph(f"<font color='red'><b>IC:</b></font> {IC_name}", styles['Normal'])],
        [Paragraph(f"<font color='red'><b>Total Students:</b></font> {student_count}", styles['Normal'])]
    ]

    # Add header spacing
    elements.append(Spacer(1, 0.1 * inch))

    # Convert header data into a table
    header_table = PlatypusTable([[header_data]])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
    ]))
    elements.append(header_table)

    # Add space after the student count
    elements.append(Spacer(1, 0.05 * inch))

    # Drop columns not needed in the seating table
    df = df.drop(columns=['Course'])
    df.insert(0, 'Serial No', range(1, len(df) + 1))  # Serial number starts from 1
    
    pdf_df = df 
    pdf_df = pdf_df.drop(columns=['Email', 'System ID'])

    pdf_df = pdf_df[['Serial No','Student ID','Student Name','Room','Seat Number']] #reordering so ID in front, change later: optimize
    
    # Add a "Signature" column for student signatures
    pdf_df['Signature'] = ''  # Empty column for signature

    # Convert the DataFrame to a list of lists for the ReportLab Table
    data = [pdf_df.columns.tolist()] + pdf_df.values.tolist()

    # Create the seating table
    table = Table(data, repeatRows=1)

    # Add table styling
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),          # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),     # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                 # Align text to center
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),       # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),                # Padding for the header row
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),        # Background color for other rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),           # Adding grid lines to make table lines prominent
    ])
    table.setStyle(style)

    # Add alternating row colors
    for i in range(1, len(data)):
        bg_color = colors.beige if i % 2 == 0 else colors.white
        style.add('BACKGROUND', (0, i), (-1, i), bg_color)
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
        pdf = SimpleDocTemplate(output_path, pagesize=letter)
    except Exception as e:
        # Handle the error and fallback to a default path
        print(f"Error occurred while creating the PDF at the specified path: {e}")
        if course_num in errors_dict:
            # If the value is not already a list, convert it to a list
            if not isinstance(errors_dict[course_num], list):
                errors_dict[course_num] = [errors_dict[course_num]]
            # Append the new error to the list
            errors_dict[course_num].append(f"Create Attendance PDF & {e}")
        else:
            # If course doesn't exist, create a new key-value pair
            errors_dict[course_num] = e


        output_path = f"Output\\Student Seating\\{course_name}_Seating_Plan_{room_num}.pdf"
        pdf = SimpleDocTemplate(output_path, pagesize=letter)
    


    # Add the table to the PDF
    elements.append(table)

    # Build the PDF
    pdf.build(elements)
    print(f"Created {course_num} PDF for room: {room_name}!")
    return output_path


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

