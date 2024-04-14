FROM scrapinghub/splash

COPY main.py /app/main.py
WORKDIR /app
RUN pip install requests

CMD ["python", "-u", "main.py"]
