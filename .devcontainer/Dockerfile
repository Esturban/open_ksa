# Use the official Python image as a parent image
FROM python:3.12.1-bullseye

# Set the working directory in the container
WORKDIR /workspace

# Copy the requirements.txt file into the container at /workspace
COPY requirements.txt /workspace/

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install requests urllib3 python-dotenv openai

# Copy the rest of the current directory contents into the container at /workspace
COPY . /workspace