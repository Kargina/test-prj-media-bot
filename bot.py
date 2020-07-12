import logging
from aiogram import Bot, Dispatcher, executor, types
import dlib
import tempfile
import os
import shutil
import ffmpeg

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("TELEGRAM_TOKEN", "")
if not api_key:
    logging.info("Please set env var TELEGRAM_TOKEN")
    exit(1)

bot = Bot(token=api_key)
dp = Dispatcher(bot)


@dp.message_handler(content_types=types.ContentTypes.VOICE)
async def process_voice(message: types.Message):
    """Convert voice messages to wav format with sample rate 16kHz"""
    destination_dir = os.path.join(FILE_PATH, "data", "audio", str(message.from_user.id))

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, f'{message.from_user.id}.oga')
        await message.voice.download(destination=tmp_file)

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        next_file_num = len(os.listdir(destination_dir))
        destination_path = os.path.join(destination_dir, f'audio_message_{next_file_num}.wav')

        stream = ffmpeg.input(tmp_file)
        stream = ffmpeg.output(stream, destination_path, ar='16000')
        ffmpeg.run(stream)

    with open(destination_path, 'rb') as audio:
        await message.answer_document \
            (audio, caption='Audio was saved.\n'
                            'This is your file converted to wav with sample rate 16kHz')


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def process_photo(message: types.Message):
    """Search faces within a photo. Save photo if face presence."""
    with tempfile.TemporaryDirectory() as tmp_dir:

        tmp_path = os.path.join(tmp_dir, f'{message.photo[-1].file_id}.jpg')
        await message.photo[-1].download(destination=tmp_path)

        detector = dlib.get_frontal_face_detector()
        img = dlib.load_rgb_image(tmp_path)
        face_list = list(detector(img, 1))

        if face_list:
            destination_path = os.path.join(FILE_PATH, "data", "photos")
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
            shutil.move(tmp_path, destination_path)
            await message.answer(f"Detected faces: {len(face_list)}.\nPhoto saved.")

        else:
            await message.answer(f"No faces found")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
