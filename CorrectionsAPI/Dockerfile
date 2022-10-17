# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.9-appservice
FROM mcr.microsoft.com/azure-functions/python:3.0-python3.9

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

RUN apt update
RUN apt install wget ca-certificates
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
# RUN apt-get install -y mysql-common=5.5.47
# RUN apt-get install -y mysql-client=5.5.47
# RUN apt-get install -y mysql-server-5.5
# RUN apt-get install -y mysql-server mysql-client
RUN apt-get install -y postgresql postgresql-contrib
RUN apt-get install -y gcc

COPY requirements.txt /
RUN pip cache purge
RUN pip install -r /requirements.txt


COPY . /home/site/wwwroot
