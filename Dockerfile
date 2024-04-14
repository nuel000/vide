FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/scrapinghub/splash/releases/download/3.5/splash_3.5_amd64.deb && \
    dpkg -i splash_3.5_amd64.deb

COPY main.py /app/main.py
WORKDIR /app
RUN pip install requests

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
