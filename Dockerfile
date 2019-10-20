FROM python:3.7-alpine

RUN apk add --no-cache --update \
    bash \
    curl \
    gcc \
    git \
    libffi-dev \
    libjpeg \
    libjpeg-turbo-dev \
    libwebp-dev \
    linux-headers \
    musl \
    musl-dev \
    neofetch \
    redis \
    zlib \
    zlib-dev

WORKDIR /usr/src/app/TG-UserBot/

# RUN git clone https://github.com/kandnub/TG-UserBot.git /usr/src/app/TG-UserBot/

# COPY ./start.sh ./config.ini* ./userbot.session* /usr/src/app/TG-UserBot/

COPY . /usr/src/app/TG-UserBot/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-warn-script-location --no-cache-dir -r requirements.txt

CMD ["bash", "start.sh"]