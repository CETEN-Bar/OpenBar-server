FROM python:3 

RUN mkdir /opt/apt
COPY user/requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app 

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY user/ /opt/app

RUN export FLASK_APP=app.py:create_app

EXPOSE 6200
ENTRYPOINT ["flask" , "run", "-p", "5000", "--host=0.0.0.0"]
