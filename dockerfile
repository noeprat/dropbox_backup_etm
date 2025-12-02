# Use an official Python runtime as a parent image
FROM python:3.12.8

# Set the working directory in the container
WORKDIR /usr/code/dropbox-sort

# Copy the current directory contents into the container at /usr/code/dropbox-sort
COPY . .

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container (Optional, only for web apps)
# EXPOSE 80

# Define environment variable (optional)
#ENV NAME World

# Run app.py when the container launches
CMD ["python", "./main.py"]