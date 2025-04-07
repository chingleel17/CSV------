# Use the official Python image as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=find_duplicates_web/app.py

# Run the application
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000","--reload"]
CMD ["gunicorn", "--reload", "-b", "0.0.0.0:5000", "find_duplicates_web.app:app"]