# https://0xacab.org/pixelated/pixelated-user-agent/container_registry
# Build with:
#   docker build -t 0xacab.org:4567/pixelated/pixelated-user-agent/buildpackage:latest .
#   docker login 0xacab.org:4567
#   docker push 0xacab.org:4567/pixelated/pixelated-user-agent/buildpackage:latest

FROM 0xacab.org:4567/leap/gitlab-buildpackage:build_jessie_amd64
COPY files/apt/deb.nodesource.com.gpg /tmp/deb.nodesource.com.gpg
RUN apt-key add /tmp/deb.nodesource.com.gpg

RUN echo 'deb http://deb.nodesource.com/node_6.x jessie main' > /etc/apt/sources.list.d/node.list
RUN apt-get update
RUN apt-get -y dist-upgrade

RUN apt-get -y install wget
RUN wget https://github.com/pixelated/pixelated-user-agent/releases/download/1.0_beta1/pixpybuild_0.2.4-190.gbpac5d78_amd64.deb
RUN dpkg -i pixpybuild_0.2.4-190.gbpac5d78_amd64.deb || /bin/true
RUN apt-get -y -f install

# override custom vars from LEAP
COPY files/custom-vars /usr/local/sbin/custom-vars
