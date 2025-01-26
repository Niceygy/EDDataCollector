FROM python:3.7-slim

# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install sqlalchemy pymysql

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Run app.py when the container launches
CMD ["python", "main.py"]