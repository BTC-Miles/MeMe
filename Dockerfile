#Download base image ubuntu 20.04
FROM ubuntu:22.04 

RUN apt update && apt install python3 python3-pip python3-setuptools -y

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r /app/requirements.txt

COPY ./server.py  ./
COPY .env ./
COPY redis_db.py ./
COPY analytics.py ./
COPY find_link.py ./
COPY get_addr_list.py ./
COPY get_token_info.py ./
COPY auth.py ./

CMD ["python3","/app/server.py"]
