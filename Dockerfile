FROM tensorflow/tensorflow

RUN mkdir -p /home/FLS

COPY ./Node /home/FLS/Node
COPY ./FLM /usr/local/lib/python3.6/dist-packages/FLM

CMD ["python", "/home/FLS/Node/main.py"]