FROM python:3.12-slim

WORKDIR /code

# docker will not re-pip install if requirements.txt doesn't change
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ADD . /code

# single worker: game state lives in-memory in one process
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:8080", "web.app:app"]
