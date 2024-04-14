FROM scrapinghub/splash

RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install requests

COPY main.py /app/main.py
WORKDIR /app

ENV PYTHONUNBUFFERED=1

CMD ["python3", "main.py"]
