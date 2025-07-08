FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y --no-install-recommends awscli && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["python3", "app.py"]