FROM python:3.7

ADD ./ /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "api_service.wsgi:app"]