FROM scrapinghub/splash

COPY main.py /app/main.py
WORKDIR /app
RUN pip install requests

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
