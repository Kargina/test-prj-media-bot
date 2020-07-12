FROM kargina/python-dlib:latest
RUN apt-get update && apt-get install -y ffmpeg
COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT python bot.py
