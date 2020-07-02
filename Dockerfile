FROM python:3.7

ENV PYTHONBUFFERED 1

RUN mkdir /src
WORKDIR /src

COPY . /src
RUN pip install -r requirements.txt

EXPOSE 80

CMD ["/bin/bash", "start_api.sh"]
