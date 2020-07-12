FROM kargina/python-dlib:latest
RUN apt-get update && apt-get install -y ffmpeg
COPY bot.py /app/bot.py
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ENTRYPOINT python /app/bot.py
