FROM ubuntu:18.04

RUN apt-get upgrade -y && apt-get update -y \
    && apt-get install python3-pip -y

RUN pip3 install flask
RUN pip3 install flask-wtf
RUN pip3 install email_validator
RUN pip3 install wtforms[email]
RUN pip3 install flask-sqlalchemy
RUN pip3 install flask-bcrypt
RUN pip3 install flask-login
RUN pip3 install Pillow
RUN pip3 install flask-mail
RUN apt-get install curl -y \
    && apt-get install nano
WORKDIR /shared
