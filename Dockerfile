FROM python:3.12-slim

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 8000
