Seat Allocation Software

📌 Project Overview

This project is a Seat Allocation Software designed to generate seating arrangements for BITS Pilani examinations. It allows users to allocate students into rooms based on course schedules and provides the option for serial or randomized seating within rooms or zones. The software also generates PDF seating plans for instructors and students.
NOTE: Data files have been removed for security reasons. 

🚀 Features

- **Multiple Allocation Modes**:
  - By Time Slot
  - By Course Number
  - All Courses on a Given Date
  - All Courses for All Dates

- **Seating Arrangement**:
  - Serial Seating (in roll number order)
  - Randomized Seating (within rooms or predefined zones)
  - Zone-based allocation

- **Output Generation**:
  - Individual room PDFs with student seating
  - Combined PDF for all rooms
  - Error logging and validation
  - Input format validation
## Code Documentation

- For detailed code documentation and developer guide, see [CODE_STRUCTURE.md](CODE_STRUCTURE.md)

## 🛠️ Prerequisites

- Python 3.8 or higher
- Node.js 16.x or higher (for frontend)
- pip (Python package manager)
- npm or yarn (Node package manager)

## Set Up

### Option 1: One-Click Start (Recommended)

1. Double-click the `start.bat` file in the project root
2. Wait for both backend and frontend to start (this may take a few minutes on first run)
3. The application should automatically open in your default browser at http://localhost:5173
4. To stop the application, press Q in the frontend window

If the browser doesn't open automatically, you can manually navigate to http://localhost:5173

### Option 2: Manual Set Up
#### 1. Clone the Repository
```bash
git clone https://github.com/ishitagod/Seating-Allocation-Software.git
cd Seating-Allocation-Software
```

#### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../exam-seating-app

# Install dependencies
npm install
```

#### 4. Configure Environment
Create a `.env` file in the `backend` directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
OUTPUT_FOLDER=./Output
```

### 🚀 Running the Application

#### Start Backend Server
```bash
# From backend directory
python app.py
```

#### Start Frontend Development Server
```bash
# From exam-seating-app directory
npm run dev
```

Access the application at: http://localhost:3000

## 📂 Project Structure

```
Seating-Allocation-Software/
├── backend/               # Backend Python code
│   ├── data/             # Sample data files
│   ├── Output/           # Generated output files
│   ├── app.py            # Main Flask application
│   ├── allocate.py       # Core allocation logic
│   └── requirements.txt  # Python dependencies
├── exam-seating-app/     # Frontend React application
└── README.md             # This file
```

## For users

1. **Input Files**:
   - `erpdata.xlsx`: Student registration data
   - `input-file-rooms.xlsx`: Room capacity and details
   - `ICS.xlsx`: Exam schedule
   - `room_data`: Folder containing room capacity and seating arrangement. (UPLOAD IS OPTIONAL)

2. **Upload Files**:
   - Use the web interface to upload the required files
   - Alternatively, place 'Room Data' folder in the `backend/data/` directory

3. **Generate Seating Plan**:
   - Select allocation criteria (by course, date, etc.)
   - Choose seating mode (serial/random/randomized in zones)
   - Click "Generate" to create seating arrangements

4. **Download Results (ZIP)**:
   - Download individual room PDFs
   - Or download combined PDF for all rooms

## Troubleshooting

- **Port Already in Use**: If port 8000 is in use, update the port in `app.py` and frontend API calls
- **Missing Dependencies**: Ensure all Python and Node.js dependencies are installed
- **File Permissions**: Ensure the application has write access to the Output directory