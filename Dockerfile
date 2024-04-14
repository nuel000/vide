FROM scrapinghub/splash

COPY main.py /app/main.py
WORKDIR /app
RUN pip install requests

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
