# Use an official Python runtime as a parent image
FROM python:3.8-slim
RUN apt-get -y update && apt-get install dos2unix && apt-get install nano
RUN useradd --create-home --shell /bin/bash app_user
# Set the working directory in the container
WORKDIR /home/app_user
USER app_user

# Copy the current directory contents into the container at /usr/src/app
COPY . .
CMD ["bash"]

