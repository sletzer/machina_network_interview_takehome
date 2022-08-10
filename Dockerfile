ARG PYTHON_VERSION=3.10.6
FROM python:${PYTHON_VERSION}

#install ifconfig & ping for QOL purposes
RUN apt update && apt install -y \
    net-tools \
    iputils-ping \
    vim

#install any pthon dependencies
RUN pip install pyzmq

#copy all files & dir from the cwd into /root on the container
ADD . /root/

#set working dir to where we just copied the source files
WORKDIR /root/

#default if no explicit arguments are passed to docker run,
#then just create a bash shell
CMD /bin/bash