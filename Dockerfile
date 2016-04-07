from ubuntu:16.04

RUN apt-get update && \
    apt-get install -y --force-yes \
    python3 \
    python3-dev \
    python3-pip \
    python3-numpy \
    git

COPY . /app/
RUN python3 -m pip install -U pip setuptools && \
    python3 -m pip install -r /app/requirements.txt

EXPOSE 8080 8888

WORKDIR /app
CMD ["bash", "entrypoint.sh"]
