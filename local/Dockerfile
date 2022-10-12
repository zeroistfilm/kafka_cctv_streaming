
FROM python:3.9

COPY resolv.conf /etc/resolv.conf


WORKDIR /home
COPY . .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt
RUN apt-get update
RUN apt-get -y install vim iputils-ping net-tools libgl1-mesa-glx

CMD ['uvicorn', 'producer:app' ,'--host','0.0.0.0']
