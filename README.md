# Media bot

## Description

This is simple telegram bot.  
Bot was realized as a test project.

Bot can:  

- save audio messages and convert to wav with sample rate 16kHz
- detect images with faces and save them

## Run with docker

```bash
git clone https://github.com/Kargina/test-prj-media-bot.git
cd test-prj-media-bot
docker build . -t bot
docker run -d -e TELEGRAM_TOKEN=<YOUR_TOKEN> -v <PATH_TO_LOCAL_DATA_FOLDER>:/app/data bot
```
