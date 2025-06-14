# Base image with Python
FROM python:3.11-slim

# Install system dependencies (Tesseract etc.)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    build-essential \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy everything from the local directory to the container's /app
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the default Render port
EXPOSE 10000

# Run the FastAPI app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]

