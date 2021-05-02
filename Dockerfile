# Base Image
FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app
COPY ./app/us_postal_codes.csv /app/us_postal_codes.csv
COPY requirements.txt /app/requirements.txt
ENV FLASK_APP=main
# Instalar dependencias de python
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt
RUN pip3 install --upgrade setuptools
