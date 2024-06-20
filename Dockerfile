# Use an official Python runtime as a parent image
FROM python:3.9-slim
RUN apt-get -y update
# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

