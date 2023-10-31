FROM python:alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install updates and necessary modules
RUN apk update && apk add libpq
# updates the repositories and installs the libpq library needed to connect to PostgreSQL.
RUN apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
# installs dependencies necessary to compile some Python modules and libraries.

RUN pip install --upgrade pip

# Install packages for the project
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

RUN apk del .build-deps

COPY . .

RUN chmod -R 777 ./
# sets access rights to 777 for all files and directories inside the container. This can be useful for debugging 
# and testing, but is not recommended for production environments as it may lead to security vulnerabilities.