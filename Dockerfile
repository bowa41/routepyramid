# Use the official Python base image
FROM python:3.12

# Set environment variables to avoid buffering of logs
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install libpq-dev and any other necessary build tools
# Update package lists and install the package, then clean up
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /app/

# Copy the .pem file to the working directory
COPY /myec2key.pem /app/myec2key.pem

# Set permissions on the .pem file if necessary
RUN chmod 600 /app/myec2key.pem

# Expose port 5000 for the Flask application
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "main.py"]
