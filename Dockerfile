FROM cellofellow/rpi-arch

RUN pacman --noconfirm -Syu 

# install dependencies
RUN pacman --noconfirm -S python python-pip git

# add psips
ADD lib/psips/bin/psips /usr/bin/

# add raspberry pi firmware libraries
ADD lib/opt/ /opt/

# add library reference to ldconfig
ADD lib/00-raspberrypi-firmware.conf /etc/ld.so.conf.d/

# register mmal library with ldd
RUN ldconfig

RUN git clone https://github.com/monsendag/rpi-cameraserver.git /app

# install picamera
RUN cd /app && pip install -r requirements.txt

# start video server
CMD /app/server.py
