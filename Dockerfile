FROM tensorflow/tensorflow

RUN mkdir -p /home/FLS

COPY ./Node /home/FLS/Node
COPY ./FLM /home/FLS/packages/FLM

ENV PYTHONPATH="$PYTHONPATH:/home/FLS/packages"

RUN pip install --no-cache-dir -r /home/FLS/Node/requirements.txt

CMD ["python", "/home/FLS/Node/main.py"]