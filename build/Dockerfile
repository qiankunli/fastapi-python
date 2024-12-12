FROM python:xx

ARG USE_CHINA_MIRROR=false

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

EXPOSE 7861

ENV PYTHONUNBUFFERED 1

WORKDIR /server

# fake debug address, 防止 chrome 启动报错
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

COPY ./backend/requirements.txt .
RUN pip3 install -r /server/requirements.txt --no-cache-dir
COPY build/entrypoint.sh /entrypoint.sh
COPY ./backend .

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
