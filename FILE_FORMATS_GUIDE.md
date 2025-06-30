# Seating Allocation Software - File Formats Guide

This document outlines the required formats for the Excel files used in the Seating Allocation Software.

## 1. ERP Data File

**File Name**: `erpdata.xlsx`
**Location**: `backend/data/`


### Sample Data:

| Campus ID | ID      | Name          | Email                   | Subject_Catalog |
|-----------|---------|---------------|-------------------------|-----------------|
| 2020A7PS | 1234567 | John Doe      | john.doe@example.com    | CS F111         |
| 2020B2PS | 2345678 | Jane Smith    | jane.smith@example.com  | PHY F111        |
| 2020C5PS | 3456789 | Alice Johnson | alice.j@example.com     | CS F111         |

### Required Columns:
1st Row according to generated Excel contains `Course Wise Reg. Student List`
- `Semester`: Semester code (e.g., 1161)
- `Career`: Career code (e.g., 0001)
- `Descr`: Semester description (e.g., "SECOND SEMESTER 2024-2025")
- `Campus ID`: Student's campus identification number (e.g., 2024A3IS0101G)
- `ID`: Student's ID (e.g., 31120240101)
- `Name`: Student's full name (e.g., NISHOK P .)
- `Subject`: Course subject code (e.g., BIO)
- `Catalog`: Course catalog number (e.g., F110)
- `Email`: Student's email address

### Sample Data:

| Semester | Career | Descr | Campus ID | ID | Name | Subject | Catalog | Email |
|----------|--------|--------------------------------|---------------|------------|-------------------|---------|---------|-----------------------------------|
| 1161 | 0001 | SECOND SEMESTER 2024-2025 | 2024A3IS0101G | 31120240101 | John Doe | BIO | F110 | john.doe@example.com |
| 1161 | 0001 | SECOND SEMESTER 2024-2025 | 2024A3IS0105G | 31120240105 | Alice Johnson . | BIO | F110 | alice.j@example.com |


## 2. Room Data File

**File Name**: `input-file-rooms.xlsx`
**Location**: `backend/data/`

### Required Columns:
- `courseno`: Course number (e.g., "CS F111")
- `No. of students`: Number of students enrolled in the course
- `Number of Rooms`: Number of rooms required for the course
- `IC`: Instructor-in-Charge name
- `COURSE TITLE`: Full course title
- `Date`: Exam date (DD/MM/YYYY)
- `Time`: Exam time slot (e.g., "09:00 AM - 12:00 PM")
- `Rooms`: Room allocation with capacities (e.g. "LT1(50),LT2(50)")

### Sample Data:
| courseno | No. of students | Number of Rooms | IC         | COURSE TITLE        | Date       | Time                | Rooms               |
|----------|-----------------|-----------------|------------|---------------------|------------|---------------------|--------------------|
| CS F111  | 120             | 2               | Dr. Smith  | Computer Programming| 15/11/2023 | 09:00 AM - 12:00 PM | LT1(60),LT2(60)    |
| PHY F111 | 90              | 1               | Dr. Brown  | Physics I           | 16/11/2023 | 02:00 PM - 05:00 PM | DLT5(90)           |

## 3. Instructor (IC) Details

**File Name**: `ICS.xlsx`
**Location**: `backend/data/`

### Required Columns:
- `Course Code`: Course code (e.g., "CS F111")
- `Course Title`: Full course title
- `IC Name`: Instructor-in-Charge name
- `IC Email`: Instructor's email
- `Department`: Department name

### Sample Data:

| Subject | Catalog | Course Title           | Display Name     | Email            | PSRN    | Subject_Catalog |
|---------|---------|------------------------|------------------|------------------|---------|-----------------|
| BIO     | F110    | XXXXXXXXXXXXX  | Jane Doe  | jane.doe@example.com   | G0XX6   | BIO F110        |
| BIO     | F215    | YYYYYYYYYYYY            | John Doe     | john.doe@example.com     | G0XX2   | BIO F215        |

## 4. Room Data Files (Optional)

**Location**: `backend/data/room_data/`

### Types of Room Files:
1. **Lecture Theaters (LT1-LT4)**: `LT1_HardLimit.xlsx`, `LT1_SoftLimit.xlsx`, etc.
2. **DLT Rooms**: `DLT5.xlsx`, `DLT6.xlsx`, etc.
3. **CC Labs**: `CCLab_HardLimit.xlsx`, `CCLab_SoftLimit.xlsx`
4. **Classrooms**: `Classrooms.xlsx`

### Required Format:
Each room file should contain seating arrangement details with the following columns:
- `Seat Number`: Physical seat number in the room
- `Row`: Row identifier (if applicable)
- `Column`: Column identifier (if applicable)
- `Block`: Block/section of the room (if applicable)
- `Status`: Seat status (Available/Reserved)


## Notes
- All dates should be in DD/MM/YYYY format
- Times should be in 12-hour format with AM/PM
- Ensure there are no merged cells in the data range
- Remove any password protection from the files
- Avoid using special characters in file names

For any questions or support, please contact the system administrator.
