FROM ubuntu:14.04
MAINTAINER Vanessa Feng <vanessa.w.feng@gmail.com>

RUN apt-get update

# install useful system tools and libraries
RUN apt-get install -y libfreetype6-dev && \
    apt-get install -y libglib2.0-0 \
                       libxext6 \
                       libsm6 \
                       libxrender1 \
                       libblas-dev \
                       liblapack-dev \
                       gfortran \
                       libfontconfig1 --fix-missing

RUN apt-get install -y tar \
                       git \
                       curl \
                       nano \
                       wget \
                       dialog \
                       net-tools \
                       build-essential

RUN apt-get install -y python \
                       python-dev \
                       python-distribute \
                       python-pip \
                       python-numpy \
                       python-scipy


# complete Python image
RUN useradd -d /app -m app
RUN chown -R app:app /app/


COPY ./requirements.txt /app
RUN cd /app && pip install -r requirements.txt
RUN pip install supervisor
RUN pip install gunicorn
RUN pip install requests

RUN pip install unidecode
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader punkt
RUN pip install flask-cors
RUN pip install flask-json

# copy over app and data
COPY . /app

# copy over config
COPY ./config /app/config
RUN chown -R app:app /app/


# Deploy service configuration
RUN cp /app/config/supervisord/supervisord.conf /etc/
RUN mkdir -p /etc/supervisord/conf.d/
RUN cp /app/config/supervisord/apps.conf /etc/supervisord/conf.d/

#Expose ports and start supervisord
EXPOSE 5011
CMD ["supervisord", "-n"]
#WORKDIR /app/src
#CMD ["python", "main.py"]