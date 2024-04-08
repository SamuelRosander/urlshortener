FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0", "urlshortener:create_app()"]
