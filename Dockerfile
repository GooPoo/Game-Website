FROM python:3.12

RUN apt-get update && apt-get install -y git

WORKDIR /usr/src/app/game-app

RUN git clone https://github.com/GooPoo/Game-Website.git .

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "wordle.py"]
