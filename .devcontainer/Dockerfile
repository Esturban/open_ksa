# Use the official Python slim image as a parent image
FROM python:3.12.1-bullseye

# Set the working directory in the container
WORKDIR /workspace

# Copy the requirements.txt file into the container at /workspace
COPY requirements.txt /workspace/

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /workspace