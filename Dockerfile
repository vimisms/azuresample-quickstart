FROM python

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]

