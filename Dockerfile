FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow

WORKDIR /app

COPY . /app/

RUN apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    pip install -r requirements.txt

CMD ["python", "bot.py"]
