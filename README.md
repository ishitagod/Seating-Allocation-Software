Seat Allocation Software

📌 Project Overview

This project is a Seat Allocation Software designed to generate seating arrangements for BITS Pilani examinations. It allows users to allocate students into rooms based on course schedules and provides the option for serial or randomized seating within rooms or zones. The software also generates PDF seating plans for instructors and students.

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

## 🛠️ Prerequisites

### Option 1: Manual Setup
- Python 3.8 or higher
- Node.js 16.x or higher (for frontend)
- pip (Python package manager)
- npm or yarn (Node package manager)

### Option 2: Docker Setup (Recommended)
- Docker Desktop (for Windows/macOS) or Docker Engine (for Linux)
- Docker Compose (usually comes with Docker Desktop)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ishitagod/Seating-Allocation-Software.git
cd Seating-Allocation-Software
```

### 2. Backend Setup
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

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../exam-seating-app

# Install dependencies
npm install
```

### 4. Configure Environment
Create a `.env` file in the `backend` directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
OUTPUT_FOLDER=./Output
```

## 🚀 Running the Application

### Seating Allocation Software

A web application for generating seating arrangements for BITS Pilani examinations.

## Features

- Upload Excel files for rooms, exams, and student data
- Generate seating arrangements based on different criteria
- Download results as Excel files
- Simple and intuitive user interface

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

## Getting Started

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the Flask server:
   ```bash
   flask run --port=8000
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd exam-seating-app
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:5173`

## Usage

1. Fill in the output file name
2. Upload the required Excel files:
   - Rooms-Exams file
   - ERP Student Data
   - ICs Data
3. Select exam type and output mode
4. Click "Generate Seating Arrangement"
5. Download the results when processing is complete

## Project Structure

```
.
├── backend/               # Flask backend
│   ├── app.py             # Main application
│   ├── requirements.txt   # Python dependencies
│   └── ...
├── exam-seating-app/      # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.tsx       # Main component
│   │   └── ...
│   └── ...
├── README.md
```
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