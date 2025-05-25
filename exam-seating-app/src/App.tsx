import React, { useState, useEffect } from "react";
import api from "./utils/api";
import Dropdown, { DropdownOption } from "./components/Dropdown";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";
import "bootstrap-icons/font/bootstrap-icons.css";
import bitsLogo from "./assets/bits-logo-nobground.png";

const pageStyle: React.CSSProperties = {
  minHeight: "100vh",
  background: "linear-gradient(135deg, #f8fafc 0%, #e7eaf6 100%)",
  padding: "2rem 0",
};

function App() {
  // File Upload States
  const [resultMsg, setResultMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [roomsExamsFile, setRoomsExamsFile] = useState<File | null>(null);
  const [erpDataFile, setErpDataFile] = useState<File | null>(null);
  const [icsDataFile, setIcsDataFile] = useState<File | null>(null);
  const [roomDataFiles, setRoomDataFiles] = useState<File[]>([]);
  const [showRoomDataUpload, setShowRoomDataUpload] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);
  const [showRoomDataWarning, setShowRoomDataWarning] = useState(false);
  const [roomDataFolderName, setRoomDataFolderName] = useState<string>('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [showRoomUploadSuccess, setShowRoomUploadSuccess] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleRefresh = async () => {
    if (!window.confirm('Are you sure you want to clear all previous outputs? This action cannot be undone.')) {
      return;
    }
    
    try {
      setLoading(true);
      const response = await api.post('/clear-output');
      
      if (response.data.success) {
        const message = response.data.cleared_files > 0 
          ? `✅ Successfully cleared ${response.data.cleared_files} file(s) from output folder`
          : 'ℹ️ ' + response.data.message;
        
        setResultMsg(message);
        setShowSuccess(true);
        // Auto-hide success message after 5 seconds
        setTimeout(() => setShowSuccess(false), 5000);
      }
    } catch (error: any) {
      console.error('Error clearing output files:', error);
      
      // Handle different types of errors
      let errorMessage = 'Failed to clear output folder';
      if (error.response) {
        // Server responded with an error status code
        if (error.response.status === 404) {
          errorMessage = 'Output folder does not exist';
        } else if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Please check your connection.';
      }
      
      setErrorMessage(errorMessage);
      setShowError(true);
      // Auto-hide error message after 5 seconds
      setTimeout(() => {
        setShowError(false);
        setErrorMessage('');
      }, 5000);
    } finally {
      setLoading(false);
    }
  };

  // Exam Type Options
  const examOptions: DropdownOption[] = [
    { value: "midsem", label: "Midsem" },
    { value: "comprehensive", label: "Comprehensive" },
  ];
  const [examType, setExamType] = useState<string>("midsem");

  // Seating Options
  const seatingArrangementOptions: DropdownOption[] = [
    { value: "serial", label: "Serial" },
    { value: "random", label: "Random" },
    { value: "random_zone", label: "Randomize in Zones" },
  ];
  const [seatingArrangement, setSeatingArrangement] = useState<string>("serial");

  // Other States
  const [outputName, setOutputName] = useState<string>("");
  const [outputMode, setOutputMode] = useState<string>("all");
  const [timeSlotInput, setTimeSlotInput] = useState<string>("");
  const [dateInput, setDateInput] = useState<string>("");
  const [courseNumberInput, setCourseNumberInput] = useState<string>("");
  const outputModeOptions = [
    { value: "all", label: "All Courses" },
    { value: "time", label: "By Time Slot" },
    { value: "course_number", label: "By Course Number" },
    { value: "day", label: "All Courses in a Day" },
  ];

  // Function to handle download
  const handleDownload = async () => {
    try {
      // Create a temporary link element
      const link = document.createElement('a');
      link.href = '/api/download-output';
      link.download = 'seating_arrangement_output.zip';
      
      // Trigger the download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      setErrorMsg('Failed to download the output. Please try again.');
      console.error('Download error:', error);
    }
  };

  // Removed unused selectedExamLabel

  // Helper to format date with day
  const getFormattedDateWithDay = (dateStr: string) => {
    if (!dateStr) return "";
    const dateObj = new Date(dateStr);
    const dayNames = [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
    ];
    const dayName = dayNames[dateObj.getDay()];
    const formattedDate =
      ("0" + (dateObj.getMonth() + 1)).slice(-2) +
      "/" +
      ("0" + dateObj.getDate()).slice(-2) +
      "/" +
      dateObj.getFullYear();
    return `${formattedDate}, ${dayName}`;
  };

  // File upload handler
  const handleFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "rooms" | "erp" | "ics" | "roomData"
  ) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    switch (type) {
      case "rooms":
        setRoomsExamsFile(files[0]);
        break;
      case "erp":
        setErpDataFile(files[0]);
        break;
      case "ics":
        setIcsDataFile(files[0]);
        break;
      case "roomData":
        // Check if it's a folder by checking if any file has a webkitRelativePath
        const fileList = Array.from(files);
        if (fileList.some(file => (file as any).webkitRelativePath)) {
          setShowRoomDataWarning(true);
          setRoomDataFiles(fileList);
          setRoomDataFolderName(fileList[0].webkitRelativePath.split('/')[0]);
        } else {
          alert('Please select a folder instead of individual files');
          e.target.value = ''; // Reset the input
        }
        break;
      default:
        break;
    }
  };

  // Submit action
  // Handle page refresh or tab close
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isProcessing) {
        // Try to stop the backend process
        api.post('/stop-process')
          .catch(console.error);
        // Standard way to show confirmation dialog
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? The current operation will be stopped.';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isProcessing]);

  const handleSubmit = async () => {
    if (!roomsExamsFile || !erpDataFile || !icsDataFile) {
      alert("Please upload all required files.");
      return;
    }
    const formData = new FormData();
    formData.append("rooms_exams_file", roomsExamsFile);
    formData.append("erp_data_file", erpDataFile);
    formData.append("ics_data_file", icsDataFile);
    formData.append("exam_type", examType);
    formData.append("output_name", outputName);
    formData.append("seating_arrangement", seatingArrangement);
    formData.append("seating", seatingArrangement);
    formData.append("mode", outputMode);
    formData.append("output_mode", outputMode);

    if (outputMode === "time") {
      formData.append("date", getFormattedDateWithDay(dateInput));
      formData.append("time_slot", timeSlotInput);
    } else if (outputMode === "course_number") {
      formData.append("course_number", courseNumberInput);
    } else if (outputMode === "day") {
      formData.append("date", getFormattedDateWithDay(dateInput));
    }
    try {
    } catch (err: any) {
      // try to pull our JSON‑logged traceback if present
      console.error(err);
      const data = err.response?.data;
      const trace = data?.traceback ? `\n\nTrace:\n${data.traceback}` : "";
      setErrorMsg(`❌ ${data?.error || err.message}${trace}`);
    } finally {
      setLoading(false);
      setIsProcessing(false);
    }
  };

  return (
    <div style={pageStyle}>
      <div className="container">
        <div className="text-center mb-1">
          <img 
            src={bitsLogo} 
            alt="BITS Pilani Logo" 
            style={{ maxHeight: '200px' }} 
            className="img-fluid"
          />
        </div>
        <div className="row justify-content-center">
          <div className="col-12 col-lg-10 col-xl-8">
            {/* Header */}
            <div className="text-center mb-4">
              <h1 className="display-4 fw-bold text-primary">Seating Allocation Software</h1>
              <p className="lead">Generate seating arrangements for BITS Pilani examinations.</p>
              <div className="d-flex justify-content-center align-items-center gap-4">
                <div className="d-flex align-items-center gap-2">
                  <span className="text-muted">Exam Type:</span>
                  <Dropdown
                    options={examOptions}
                    selected={examType}
                    onSelect={setExamType}
                    buttonClassName="btn btn-outline-primary btn-sm"
                    id="examTypeHeader"
                  />
                </div>
                <button 
                  type="button" 
                  className="btn btn-outline-primary btn-sm d-flex align-items-center gap-1"
                  onClick={handleRefresh}
                  title="Clear all previous output files"
                >
                  <i className="bi bi-arrow-clockwise"></i>
                  <span>Clear Outputs</span>
                </button>
                
                {/* Success Alert */}
                {showSuccess && (
                  <div className="alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3" role="alert">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {resultMsg || 'Operation completed successfully.'}
                    <button type="button" className="btn-close" onClick={() => setShowSuccess(false)} aria-label="Close"></button>
                  </div>
                )}
                
                {/* Room Data Upload Success Alert */}
                {showRoomUploadSuccess && (
                  <div className="alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3" role="alert">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    Successfully uploaded {roomDataFiles.length} room data file(s)
                    <button type="button" className="btn-close" onClick={() => setShowRoomUploadSuccess(false)} aria-label="Close"></button>
                  </div>
                )}
                
                {/* Error Alert */}
                {showError && (
                  <div className="alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3" role="alert">
                    <strong>Error!</strong> {errorMessage || 'An error occurred.'}
                    <button type="button" className="btn-close" onClick={() => {
                      setShowError(false);
                      setErrorMessage('');
                    }} aria-label="Close"></button>
                  </div>
                )}
              </div>
            </div>

            {/* Main Form */}
            <div className="card shadow-lg rounded-4 overflow-hidden">
              <div className="card-body p-4 p-md-7">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSubmit();
                  }}
                >
                  {/* Output Name */}
                  <div className="mb-4">
                    <label className="form-label fw-semibold">
                      Output File Name
                    </label>
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      placeholder="Enter output file name"
                      value={outputName}
                      onChange={(e) => setOutputName(e.target.value)}
                      required
                    />
                    <div className="form-text">
                      This will be used as the base name for generated files
                    </div>
                  </div>

                  {/* File Uploads */}
                  <div className="row g-4 mb-4">
                    <div className="col-md-4">
                      <div className="border rounded-3 p-3 h-100">
                        <label className="form-label fw-semibold d-block">
                          <i className="bi bi-file-earmark-spreadsheet me-2"></i>
                          Rooms-Exams File
                        </label>
                        <input
                          type="file"
                          className="form-control"
                          onChange={(e) => handleFileUpload(e, "rooms")}
                          accept=".xlsx,.xls"
                          required
                        />
                        {roomsExamsFile && (
                          <div className="mt-2 text-success small">
                            <i className="bi bi-check-circle-fill me-1"></i>
                            {roomsExamsFile.name}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="col-md-4">
                      <div className="border rounded-3 p-3 h-100">
                        <label className="form-label fw-semibold d-block">
                          <i className="bi bi-people-fill me-2"></i>
                          ERP Student Data
                        </label>
                        <input
                          type="file"
                          className="form-control"
                          onChange={(e) => handleFileUpload(e, "erp")}
                          accept=".xlsx,.xls"
                          required
                        />
                        {erpDataFile && (
                          <div className="mt-2 text-success small">
                            <i className="bi bi-check-circle-fill me-1"></i>
                            {erpDataFile.name}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="col-md-4">
                      <div className="border rounded-3 p-3 h-100">
                        <label className="form-label fw-semibold d-block">
                          <i className="bi bi-file-earmark-text me-2"></i>
                          ICs Data
                        </label>
                        <input
                          type="file"
                          className="form-control"
                          onChange={(e) => handleFileUpload(e, "ics")}
                          accept=".xlsx,.xls"
                          required
                        />
                        {icsDataFile && (
                          <div className="mt-2 text-success small">
                            <i className="bi bi-check-circle-fill me-1"></i>
                            {icsDataFile.name}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="form-check form-switch mb-4">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      role="switch"
                      id="useRoomDataSwitch"
                      checked={showRoomDataUpload}
                      onChange={(e) => setShowRoomDataUpload(e.target.checked)}
                    />
                    <label className="form-check-label fw-semibold" htmlFor="useRoomDataSwitch">
                      <i className="bi bi-upload me-2"></i>
                      Upload Room Data (ZIP)
                    </label>
                  </div>

                  {showRoomDataUpload && (
                    <div className="mb-4">
                      <div className="border rounded-3 p-3">
                        <label className="form-label fw-semibold d-block">
                          <i className="bi bi-folder2-open me-2"></i>
                          Room Data Folder
                        </label>
                        <input
                          type="file"
                          className="form-control"
                          /* @ts-ignore */
                          webkitdirectory="true"
                          /* @ts-ignore */
                          directory=""
                          multiple
                          onChange={(e) => handleFileUpload(e, "roomData")}
                          required={showRoomDataUpload}
                        />
                        <div className="form-text">
                          Select a folder containing room data Excel files
                        </div>
                        {roomDataFiles.length > 0 && (
                          <div className="mt-2 text-success small">
                            <i className="bi bi-check-circle-fill me-1"></i>
                            Selected folder: {roomDataFolderName} ({roomDataFiles.length} files)
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Room Data Replacement Warning Modal */}
                  {showRoomDataWarning && (
                    <div className="modal show d-block" style={{
                      position: 'fixed',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundColor: 'rgba(0,0,0,0.5)',
                      zIndex: 1050
                    }}>
                      <div className="modal d-block" tabIndex={-1}>
                        <div className="modal-dialog">
                          <div className="modal-content">
                            <div className="modal-header">
                              <h5 className="modal-title">Replace Room Data</h5>
                              <button 
                                type="button" 
                                className="btn-close" 
                                onClick={() => setShowRoomDataWarning(false)}
                                aria-label="Close"
                              />
                            </div>
                            <div className="modal-body">
                              <p>This will replace all existing room data with the new files from the selected folder.</p>
                              <p className="fw-bold">Folder: {roomDataFolderName}</p>
                              <p>Number of files: {roomDataFiles.length}</p>
                              <p className="text-danger">This action cannot be undone. Are you sure you want to continue?</p>
                            </div>
                            <div className="modal-footer">
                              <button 
                                type="button" 
                                className="btn btn-secondary" 
                                onClick={() => {
                                  setShowRoomDataWarning(false);
                                  setRoomDataFiles([]);
                                  setRoomDataFolderName('');
                                  const inputs = document.querySelectorAll<HTMLInputElement>('input[type="file"][webkitdirectory]');
                                  inputs.forEach(input => {
                                    if (input) input.value = '';
                                  });
                                }}
                              >
                                Cancel
                              </button>
                              <button 
                                type="button" 
                                className="btn btn-primary"
                                onClick={async () => {
                                  try {
                                    setShowRoomDataWarning(false);
                                    const formData = new FormData();
                                    roomDataFiles.forEach((file) => {
                                      formData.append('room_files', file);
                                    });

                                    const response = await api.post('/upload-room-data', formData, {
                                      headers: {
                                        'Content-Type': 'multipart/form-data',
                                      },
                                    });

                                    if (response.data.success) {
                                      setShowRoomUploadSuccess(true);
                                      setRoomDataFiles([]);
                                      setRoomDataFolderName('');
                                      setTimeout(() => {
                                        setShowRoomUploadSuccess(false);
                                      }, 3000);
                                    }
                                  } catch (error) {
                                    console.error('Error uploading room data:', error);
                                    setErrorMessage('Failed to upload room data. Please try again.');
                                    setShowError(true);
                                    setTimeout(() => {
                                      setShowError(false);
                                      setErrorMessage('');
                                    }, 5000);
                                  }
                                }}
                              >
                                Confirm and Upload
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Configuration Options */}
                  <div className="row g-4 mb-4">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label fw-semibold">
                          Seating Arrangement
                        </label>
                        <Dropdown
                          options={seatingArrangementOptions}
                          selected={seatingArrangement}
                          onSelect={setSeatingArrangement}
                          buttonClassName="form-select"
                          id="seatingArrangement"
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label fw-semibold">
                          Output Mode
                        </label>
                        <Dropdown
                          options={outputModeOptions}
                          selected={outputMode}
                          onSelect={setOutputMode}
                          buttonClassName="form-select"
                          id="outputMode"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Dynamic Fields Based on Output Mode */}
                  {outputMode === "time" && (
                    <div className="row g-4 mb-4">
                      <div className="col-md-6">
                        <label className="form-label fw-semibold">Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={dateInput}
                          onChange={(e) => setDateInput(e.target.value)}
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label fw-semibold">Time Slot</label>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="e.g., 9:00 AM - 12:00 PM"
                          value={timeSlotInput}
                          onChange={(e) => setTimeSlotInput(e.target.value)}
                          required
                        />
                      </div>
                    </div>
                  )}

                  {outputMode === "course_number" && (
                    <div className="mb-4">
                      <label className="form-label fw-semibold">
                        Course Number
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Enter course number"
                        value={courseNumberInput}
                        onChange={(e) => setCourseNumberInput(e.target.value)}
                        required
                      />
                    </div>
                  )}

                  {outputMode === "day" && (
                    <div className="mb-4">
                      <label className="form-label fw-semibold">
                        Select Date
                      </label>
                      <input
                        type="date"
                        className="form-control"
                        value={dateInput}
                        onChange={(e) => setDateInput(e.target.value)}
                        required
                      />
                    </div>
                  )}

                  {/* Submit Button */}
                  <div className="d-grid mt-5">
                    <button
                      type="submit"
                      className="btn btn-primary btn-lg fw-bold py-3"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Generating...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-gear-fill me-2"></i>
                          Generate Seating Arrangement
                        </>
                      )}
                    </button>
                  </div>
                </form>
                <div className="mb-4"></div>

                {/* Result Message */}
                {resultMsg && (
                  <div className="mb-3">
                    <div className="alert alert-success" role="alert">
                      {resultMsg.split("\n").map((line, i) => (
                        <p key={i} className="mb-0">
                          {line}
                        </p>
                      ))}
                    </div>
                    
                    {/* Download Button */}
                    <div className="text-center mt-3">
                      <button
                        className="btn btn-primary btn-lg"
                        onClick={handleDownload}
                      >
                        <i className="bi bi-download me-2"></i>
                        Download Generated Files
                      </button>
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {errorMsg && (
                  <div className="alert alert-danger" role="alert">
                    {errorMsg.split("\n").map((line, i) => (
                      <p key={i} className="mb-0">
                        {line}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="text-center mt-4 text-muted small">
              <p className="mb-0">
                BITS Pilani, K. K. Birla Goa Campus - AUGSD
              </p>
              <p className="mb-0">
                For support, please contact AUGSD office.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
