# Use the official Python base image
FROM python:3.12

# Set environment variables to avoid buffering of logs
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /

# Install libpq-dev and any other necessary build tools
# Update package lists and install the package, then clean up
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the working directory
COPY requirements.txt /

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /

ENV FLASK_APP=app

# Set permissions on the .pem file if necessary
RUN chmod 600 /myec2key.pem

# Expose port 80 for the Flask application
EXPOSE 80

# Command to run the Flask application using Gunicorn
#ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "main:app"]
ENTRYPOINT ["waitress-serve", "--host", "0.0.0.0", "--port", "80", "main:app"]
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "main:app"]