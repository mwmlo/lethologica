# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /code

COPY prod-requirements.txt .

RUN pip3 install -r prod-requirements.txt

COPY . .

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app.flaskr:app"]
