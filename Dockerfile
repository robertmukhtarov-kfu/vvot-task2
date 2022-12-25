FROM ubuntu
RUN apt update && apt install -y python3 python3-pip
RUN pip3 install Pillow boto3 sanic requests ydb
COPY vvot13-face-cut.py .
CMD ["python3", "/vvot13-face-cut.py"]