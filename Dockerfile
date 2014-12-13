FROM cellofellow/rpi-arch

MAINTAINER Dag Einar Monsen "me@dag.im"

ENV REFRESHED_AT 2014-12-06

RUN pacman --noconfirm -Syu 

# install dependencies
RUN pacman --noconfirm -S python python-pip git

# add psips
ADD vendor/psips/bin/psips /usr/bin/

# add raspberry pi firmware libraries
ADD vendor/opt/ /opt/

# add library reference to ldconfig
ADD vendor/etc/ld.so.conf.d/00-raspberrypi-firmware.conf /etc/ld.so.conf.d/

# register mmal library with ldd
RUN ldconfig

# bust cache of application
ENV BUST_APP ce400be

RUN git clone https://github.com/monsendag/rpi-cameraserver.git /app

# install picamera
RUN cd /app && pip install -r requirements.txt

# export rests port
EXPOSE 5000

# start video server
CMD /app/server.py
