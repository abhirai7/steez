FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt update && apt upgrade -y 

RUN pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python", "main.py"]
