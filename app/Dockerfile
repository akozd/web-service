FROM python:3.8-slim-buster

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app.py app.py

CMD [ "sh", "-c", "gunicorn -w 4 -b :8000 app:app"]