# Use Python 3.8 as base image
FROM python:3.8-alpine

# Specify working directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy base files
COPY . .

# Set environment variables to use the cfg/db folders
ENV CONFIG_PATH /cfg/config.json
ENV DATABASE_PATH /db/database.db

# Specify run command
CMD [ "python", "-m", "bot.bot" ]