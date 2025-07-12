FROM debian:bullseye

RUN apt-get update && apt-get install -y \
    libreoffice \
    unoconv \
    python3 \
    python3-pip \
    python3-uno \
    && apt-get clean

WORKDIR /app

COPY app.py .

RUN pip3 install fastapi uvicorn python-multipart

EXPOSE 8002

CMD libreoffice --headless --accept="socket,host=0.0.0.0,port=2002;urp;" & \
    uvicorn app:app --host 0.0.0.0 --port 8002
