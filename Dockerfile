FROM python:3-alpine

RUN mkdir /app
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "./karbon-auth.py" ]