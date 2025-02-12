FROM python:slim-bullseye

# Copy the current directory contents into the container at /app
COPY . /home

# Set the working directory to /app
WORKDIR /home

# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
# Run app.py when the container launches
CMD ["python3", "main.py"]