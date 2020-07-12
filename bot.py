import logging
from aiogram import Bot, Dispatcher, executor, types
import dlib
import tempfile
import os
import shutil
import ffmpeg

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
SAMPLE_RATE = 16000
IMAGE_SCALE = 1

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("TELEGRAM_TOKEN", "")

if not api_key:
    logging.info("Env var TELEGRAM_TOKEN must be set, exit...")
    exit(1)

bot = Bot(token=api_key)
dp = Dispatcher(bot)


class MediaBotError(Exception):
    pass


def create_user_dir(dir_name, user_id):
    destination_dir = os.path.join(FILE_PATH, "data", dir_name, str(user_id))
    if not os.path.exists(destination_dir):
        try:
            os.makedirs(destination_dir)
        except OSError as e:
            logging.error(f" {destination_dir!r}: {e}")
            raise MediaBotError

    return destination_dir


@dp.message_handler(commands=['start', 'help'])
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends start/help or any message
    """
    await message.answer("Hi!\nSend me photo or voice message.")


@dp.message_handler(content_types=types.ContentTypes.VOICE)
async def process_voice(message: types.Message):
    """
    Convert voice messages to wav format with sample rate 16kHz
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = os.path.join(tmp_dir, f'{message.from_user.id}.oga')
        await message.voice.download(destination=tmp_file_path)

        try:
            destination_dir = create_user_dir('audio', message.from_user.id)
        except MediaBotError:
            await message.reply("Can't save file, sorry")
            return
        file_num = len(os.listdir(destination_dir))
        destination_path = os.path.join(destination_dir, f'audio_message_{file_num}.wav')

        stream = ffmpeg.input(tmp_file_path)
        stream = ffmpeg.output(stream, destination_path, ar=SAMPLE_RATE)
        try:
            ffmpeg.run(stream)
        except Exception as e:
            msg = "Can't decode audio file"
            logging.error(f"{msg} {tmp_file_path!r}: {e}")
            await message.reply(msg)

    try:
        with open(destination_path, 'rb') as audio:
            await message.reply_document(audio, caption='Audio was saved.\n'
                                                        'This is your file converted '
                                                        'to wav with sample rate 16kHz.')
    except IOError as e:
        logging.error(f"Can't write to file {destination_path!r}: {e}")
        await message.reply("File was decoded, but i can't save it, sorry.")


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def process_photo(message: types.Message):
    """
    Search faces within a photo. Save photo if face presence
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file_path = os.path.join(tmp_dir, f'{message.photo[-1].file_id}.jpg')
        await message.photo[-1].download(destination=tmp_file_path)

        detector = dlib.get_frontal_face_detector()
        img = dlib.load_rgb_image(tmp_file_path)
        face_list = list(detector(img, IMAGE_SCALE))

        if face_list:
            try:
                destination_dir = create_user_dir("photos", message.from_user.id)
            except MediaBotError:
                await message.reply("Can't save file, sorry")
                return
            shutil.move(tmp_file_path, destination_dir)
            await message.reply(f"Detected faces: {len(face_list)}.\nPhoto saved.")
        else:
            await message.reply(f"No faces found")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
