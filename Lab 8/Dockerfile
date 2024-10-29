# Use an official Python runtime as an image
FROM python:3.9

# Expose the port that the app runs on (Flask apps listen to port 5000 by default)
EXPOSE 5000

# Set the working directory inside the container to /lab8_example
WORKDIR /

# Copy the requirements file into the working directory
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the working directory
COPY . .

# Run app.py when the container launches
CMD python app.py
