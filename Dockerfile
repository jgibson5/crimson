FROM python:3.8.1-slim-buster

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

ARG MODE=development
ENV MODE=$MODE

ARG AWS_ACCESS_KEY
ENV AWS_ACCESS_KEY=$AWS_ACCESS_KEY

ARG AWS_SECRET_KEY
ENV AWS_SECRET_KEY=$AWS_SECRET_KEY

ENTRYPOINT [ "python" ]

CMD [ "run_app.py" ]
