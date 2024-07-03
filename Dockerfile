# Use an official Python runtime as a base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire content of your project to the working directory
COPY . .

# # # Install Playwright and download browsers
# RUN playwright install
# RUN playwright install-deps 

ENV GOOGLE_APPLICATION_CREDENTIALS=""

# Command to run your Playwright script
CMD ["python", "main.py"]
