FROM cellofellow/rpi-arch

RUN pacman --noconfirm -Syu 

# install dependencies
RUN pacman --noconfirm -S python python-pip base-devel openssh git

# install psips
RUN git clone git://github.com/AndyA/psips.git \
	&& cd psips \
	&& ./setup.sh && ./configure && make && make install

# add raspberry pi firmware libraries
ADD lib/opt/ /opt/

# add library reference to ldconfig
ADD lib/00-raspberrypi-firmware.conf /etc/ld.so.conf.d/

# register mmal library with ldd
RUN ldconfig

# install picamera
RUN pip install picamera

# start video server
CMD python /app/server.py
