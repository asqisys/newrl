FROM python:3.8-slim-buster
WORKDIR /code
COPY . /code/
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "/code/scripts/start.sh" ]
