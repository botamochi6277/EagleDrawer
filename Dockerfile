FROM python:3.8
WORKDIR /code
COPY src /code/
COPY requirements.txt /code/requirements.txt
RUN python -m pip install -U pip &&\
    python -m pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python","src/draw.py"]