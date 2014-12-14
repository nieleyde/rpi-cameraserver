FROM cellofellow/rpi-arch

MAINTAINER Dag Einar Monsen "me@dag.im"

# Bust dockerfile with git hash
# `sed -ri -e "s/(BUST_DOCKERFILE\s+).*/\1$(git rev-parse --short HEAD)/" Dockerfile`
ENV BUST_DOCKERFILE 7b439d9

RUN pacman --noconfirm -Syu 

# install dependencies
RUN pacman --noconfirm -S python python-pip git ffmpeg

# add psips
ADD vendor/psips/bin/psips /usr/bin/

# add raspberry pi firmware libraries
ADD vendor/opt/ /opt/

# add library reference to ldconfig
ADD vendor/etc/ld.so.conf.d/00-raspberrypi-firmware.conf /etc/ld.so.conf.d/

# register mmal library with ldd
RUN ldconfig

# bust application cache with git hash
# `sed -ri -e "s/(BUST_APP\s+).*/\1$(git rev-parse --short HEAD)/" Dockerfile`
ENV BUST_APP 7b439d9

RUN git clone https://github.com/monsendag/rpi-cameraserver.git /app

# install picamera
RUN cd /app && pip install -r requirements.txt

# export rests port
EXPOSE 5000

# start video server
CMD /app/server.py
