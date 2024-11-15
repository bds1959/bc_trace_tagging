# Use a Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the necessary files to the container
COPY . .
RUN ls -ltra
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your Python script
ENTRYPOINT ["python", "add_trace_id.py"]
