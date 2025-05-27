# Use official Python image (lowercase 'python', colon separator)
FROM python:3.13.3

# Set working directory
WORKDIR /Project-D

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all necessary files/directories (each COPY needs destination)
COPY AI/ ./AI/
COPY image.png .
COPY README.md .

# Expose port (optional, documentation only)
EXPOSE 8000

# Run your Python script (square brackets for CMD, no quotes)
CMD ["python", "chadbot_sigma_v1"]