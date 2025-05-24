# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Node.js and npm for frontend
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install frontend dependencies and build
WORKDIR /app/exam-seating-app
RUN npm install
RUN npm run build

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV OUTPUT_FOLDER=/app/backend/Output

# Create output directory
RUN mkdir -p ${OUTPUT_FOLDER}

# Expose the port the app runs on
EXPOSE 8000

# Set the working directory back to app root
WORKDIR /app/backend

# Command to run the application
CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=8000"]
