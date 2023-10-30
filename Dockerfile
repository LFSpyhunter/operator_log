# syntax=docker/dockerfile:1
FROM python
WORKDIR /operator_log
ENV FLASK_APP=runserver.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN cd /etc/apt/sources.list.d && echo "deb http://ftp.de.debian.org/debian sid main non-free" > mx.list
RUN apt-get update && apt-get -y install libsnmp-dev && apt-get install snmp && apt-get -y install snmp-mibs-downloader && apt-get install snmp && apt-get -y install telnet
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python", "runserver.py"]