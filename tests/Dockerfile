FROM python:3 

COPY app/requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app /opt/app/

ENTRYPOINT ["pytest"]
