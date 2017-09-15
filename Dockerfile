FROM python:3.5

MAINTAINER micheal.laraia@gmail.com

ENV SWAP_URL https://github.com/miclaraia/swap/archive/master.tar.gz

RUN apt update && apt install \
    nginx \
    && curl https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb -o /tmp/dumb-init.deb \
    && dpkg -i /tmp/dumb-init.deb && rm /tmp/dumb-init.deb \
    && pip install virtualenv

EXPOSE 443

