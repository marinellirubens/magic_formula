FROM python:3.8-slim-buster
RUN mkdir -p /magic-formula
COPY ./src /magic-formula/src
COPY ./requirements.txt /magic-formula/requirements.txt
WORKDIR /magic-formula
RUN python3 -m pip install -r requirements.txt
CMD ["/usr/local/bin/python3", "magic_formula/main.py"]
