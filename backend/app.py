from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, traceback, json, shutil, signal
from datetime import datetime
import pandas as pd
from zipfile import ZipFile
import tempfile
from pathlib import Path
from multiprocessing import Process, current_process

# Import your main processing function
from main import main as process_main

# Initialize Flask app
# app = Flask(__name__)
# CORS(app)
app = Flask(__name__)
# Allow all origins for development
CORS(app, resources={r"/*": {"origins": "*"}})

# Global variable to track the current process
current_process = None

# Define directories
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Output")

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/upload-files", methods=["POST"])
def upload_files():
    try:
        # Fetch uploaded files
        rooms_file = request.files.get("rooms_exams_file")
        erp_file = request.files.get("erp_data_file")
        ics_file = request.files.get("ics_data_file")

        # Validate
        if not (erp_file and ics_file):
            return jsonify({"error": "Missing one or more required files (ERP data and ICS file are required)."}), 400

        # Room data files are optional and stored in data/room_data
        ROOM_DATA_FOLDER = os.path.join(BASE_DIR, "data", "room_data")
        os.makedirs(ROOM_DATA_FOLDER, exist_ok=True)

        # Save to disk
        erp_path = os.path.join(UPLOAD_FOLDER, erp_file.filename)
        ics_path = os.path.join(UPLOAD_FOLDER, ics_file.filename)
        
        # Save rooms file if provided
        if not rooms_file:
            return jsonify({"error": "Rooms exam file is required."}), 400
            
        rooms_path = os.path.join(UPLOAD_FOLDER, rooms_file.filename)
        rooms_file.save(rooms_path)
        
        erp_file.save(erp_path)
        ics_file.save(ics_path)

        # Extract form parameters
        exam_type = request.form.get("exam_type")
        exam_title = request.form.get("output_name") or request.form.get("exam_title")
        seating_mode = request.form.get("seating_arrangement") or request.form.get("seating")
        output_mode = request.form.get("output_mode") or request.form.get("mode")
        date = request.form.get("date")
        
        # Log if we have any room data files available
        room_data_files = [f for f in os.listdir(ROOM_DATA_FOLDER) if f.endswith(('.xlsx', '.xls'))]
        if room_data_files:
            print(f"Found {len(room_data_files)} room data files in {ROOM_DATA_FOLDER}")
        else:
            print("No room data files found. Using only the provided rooms file.")
        time_slot = request.form.get("time_slot")
        course_number = request.form.get("course_number")

        # Create a new process
        global current_process
        
        # Terminate any existing process
        if current_process and current_process.is_alive():
            current_process.terminate()
            current_process.join()
        
        # Start a new process
        current_process = Process(
            target=process_main,
            args=(
                erp_path,
                rooms_path,
                ics_path,
                exam_type,
                exam_title,
                seating_mode,
                output_mode,
                date,
                time_slot,
                course_number
            )
        )
        current_process.start()
        current_process.join()  # Wait for the process to complete

        return jsonify({
            "message": "Files uploaded and processed successfully.",
            "output_folder": OUTPUT_FOLDER
        }), 200

    except Exception as e:
        # Capture traceback
        tb = traceback.format_exc()
        # Prepare log entry
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z",
            "error": str(e),
            "traceback": tb
        }
        # Append to JSON log
        log_file = os.path.join(OUTPUT_FOLDER, "error_log.json")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Optionally return traceback in response (for dev)
        return jsonify({"error": str(e), "traceback": tb}), 500



@app.route("/preview-output", methods=["GET"])
def preview_output():
    """
    Returns the first 5 rows of output.xlsx as JSON for preview.
    """
    excel_path = os.path.join(OUTPUT_FOLDER, "output_file.xlsx")
    if not os.path.exists(excel_path):
        return jsonify({"error": "No output.xlsx found"}), 404

    # Read the first 5 rows
    df = pd.read_excel(excel_path, nrows=5)
    data = df.to_dict(orient="records")
    columns = list(df.columns)

    return jsonify({"columns": columns, "rows": data}), 200

@app.route("/download-output", methods=["GET"])
def download_output():
    """
    Creates a zip file of the output directory and sends it for download
    """
    try:
        # Create a temporary file to store the zip
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        # Create a zip file
        with ZipFile(temp_file.name, 'w') as zipf:
            # Add all files from the output directory
            for root, _, files in os.walk(OUTPUT_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Add file to zip with relative path
                    arcname = os.path.relpath(file_path, os.path.dirname(OUTPUT_FOLDER))
                    zipf.write(file_path, arcname)
        
        # Send the file
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name='seating_arrangement_output.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the temporary file
        try:
            temp_file.close()
            os.unlink(temp_file.name)
        except:
            pass

@app.route('/clear-output', methods=['POST'])
def clear_output():
    try:
        # Ensure the output directory exists
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Check if output directory exists and has files
        if not os.path.exists(OUTPUT_FOLDER):
            return jsonify({
                "success": False,
                "error": "Output directory does not exist"
            }), 404

        # Get list of files in output directory
        files = os.listdir(OUTPUT_FOLDER)
        if not files:
            return jsonify({
                "success": True,
                "message": "Output folder is already empty",
                "cleared_files": 0
            })

        # Delete all files in the output directory
        cleared_count = 0
        errors = []
        for filename in files:
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    cleared_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    cleared_count += 1
            except Exception as e:
                error_msg = f'Failed to delete {file_path}. Reason: {str(e)}'
                print(error_msg)
                errors.append(error_msg)

        if errors:
            return jsonify({
                "success": True,
                "message": f"Cleared {cleared_count} files, but encountered {len(errors)} errors",
                "cleared_files": cleared_count,
                "error_count": len(errors),
                "errors": errors
            })

        return jsonify({
            "success": True,
            "message": f"Successfully cleared {cleared_count} files from output folder",
            "cleared_files": cleared_count
        })

    except Exception as e:
        error_msg = f'Error clearing output folder: {str(e)}'
        print(error_msg)
        return jsonify({
            "success": False,
            "error": error_msg,
            "traceback": traceback.format_exc()
        }), 500

@app.route('/upload-room-data', methods=['POST'])
def upload_room_data():
    try:
        # Ensure the room_data directory exists inside data folder
        ROOM_DATA_FOLDER = os.path.join(BASE_DIR, "data", "room_data")
        os.makedirs(ROOM_DATA_FOLDER, exist_ok=True)
        
        # Clear existing room data
        for filename in os.listdir(ROOM_DATA_FOLDER):
            file_path = os.path.join(ROOM_DATA_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        
        # Save new room data files
        if 'room_files' not in request.files:
            return jsonify({"success": False, "error": "No files provided"}), 400
            
        files = request.files.getlist('room_files')
        if not files:
            return jsonify({"success": False, "error": "No files provided"}), 400
            
        saved_files = []
        for file in files:
            if file.filename == '':
                continue
                
            # Ensure the file is an Excel file
            if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                continue
                
            # Save the file
            filename = os.path.basename(file.filename)  # Get just the filename, not the path
            file_path = os.path.join(ROOM_DATA_FOLDER, filename)
            file.save(file_path)
            saved_files.append(filename)
            
        if not saved_files:
            return jsonify({"success": False, "error": "No valid Excel files found"}), 400
            
        return jsonify({
            "success": True, 
            "message": "Successfully uploaded room data files",
            "files": saved_files
        })
        
    except Exception as e:
        print(f'Error uploading room data: {str(e)}')
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/stop-process", methods=["POST"])
def stop_process():
    global current_process
    if current_process and current_process.is_alive():
        current_process.terminate()
        current_process.join()
        current_process = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "no process running"})

def cleanup(signum, frame):
    global current_process
    if current_process and current_process.is_alive():
        current_process.terminate()
        current_process.join()
    
    # Clean up cleaned_erpdata.xlsx if it exists
    cleaned_erp_path = os.path.join(UPLOAD_FOLDER, "cleaned_erpdata.xlsx")
    if os.path.exists(cleaned_erp_path):
        try:
            os.remove(cleaned_erp_path)
            print(f"Cleaned up {cleaned_erp_path}")
        except Exception as e:
            print(f"Error cleaning up {cleaned_erp_path}: {e}")
    
    # Clean up any other resources if needed
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=False)  # debug=False by default
