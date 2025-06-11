# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-cffi \
    python3-brotli \
    libpango1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    libjpeg62-turbo-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libglib2.0-0 \
    libglib2.0-dev \
    build-essential \
    fontconfig \
    && apt-get clean

# Set environment variables
ENV LD_LIBRARY_PATH=/usr/lib:/usr/local/lib:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Set the working directory
WORKDIR /condominio_app

# Copy the application code
COPY . /condominio_app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "condominio_app.wsgi"]