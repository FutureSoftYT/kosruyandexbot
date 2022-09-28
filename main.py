import datetime

import yadisk
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

from config import BOT_TOKEN, YADISK_TOKEN

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
yandex = yadisk.YaDisk(token=YADISK_TOKEN)


async def upload_file(file_, folder):
    folder_name = folder.split('/')[0]
    is_dir = yandex.is_dir(folder_name)
    if is_dir is False:
        yandex.mkdir(folder_name)
    yandex.upload(file_, folder)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='Прямой поток')
            ],
            [
                KeyboardButton(text='Возвратный поток')
            ],
            [
                KeyboardButton(text='Отчёт')
            ]
        ]
    )

    await message.answer('Привет, Выберите куда хотите выгрузить данные', reply_markup=markup)


@dp.message_handler(text=['Прямой поток', 'Возвратный поток'], state='*')
async def potok_func(message: types.Message, state: FSMContext):
    await state.finish()
    folder = message.text
    await state.update_data(folder=folder)
    await state.set_state('potok')
    await message.answer('Отправьте файл с разширением .zip')


@dp.message_handler(text=['Отчёт'], state='*')
async def potok_func(message: types.Message, state: FSMContext):
    await state.finish()
    await state.set_state('otchet')
    await message.answer('Отправьте файл:')


@dp.message_handler(state='otchet', content_types=types.ContentType.ANY)
async def get_document(message: types.Message, state: FSMContext):
    await message.answer('Идёт загрузка...')
    file_size = 0
    file_name = 'test'
    if message.document:
        file_name = message.document.file_name
        file_size = message.document.file_size
        if file_size > 20 * 1024 * 1024:
            return await message.answer('Размер файла превышает лимиты телеграмма!')
        await message.document.download(destination_file='files/documents/' + file_name)

    if message.photo:
        file_size = message.photo[-1].file_size
        if file_size > 20 * 1024 * 1024:
            return await message.answer('Размер файла превышает лимиты телеграмма!')
        file_name = message.photo[-1].file_id
        await message.photo[-1].download(destination_file='files/documents/' + file_name)

    if message.video:
        file_name = message.video.file_name
        file_size = message.video.file_size
        if file_size > 20 * 1024 * 1024:
            return await message.answer('Размер файла превышает лимиты телеграмма!')
        await message.video.download(destination_file='files/documents/' + file_name)

    folder_name = 'Отчёт'

    date = str(datetime.datetime.now()).split('.')[0]
    await upload_file('files/documents/' + file_name,
                      folder_name + '/' + f'[{date.replace(":", ".")}]' + file_name)

    await message.answer('Файл загружен!')

    await state.finish()


@dp.message_handler(state='potok', content_types=types.ContentType.DOCUMENT)
async def get_document(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    folder_name = state_data.get('folder')

    file_name = message.document.file_name

    if message.document.file_size < 20 * 1024 * 1024:

        await message.document.download(destination_file='files/documents/' + file_name)
        date = str(datetime.datetime.now()).split('.')[0]
        await upload_file('files/documents/' + file_name,
                          folder_name + '/' + f'[{date.replace(":", ".")}]' + file_name)

        await message.answer('Файл загружен!')
    else:
        await message.answer('Размер файла превышает лимиты телеграмма!')
    await state.finish()


@dp.message_handler(state='potok', content_types=types.ContentType.PHOTO)
@dp.message_handler(state='potok', content_types=types.ContentType.VIDEO)
async def get_document_unsuported(message: types.Message, state: FSMContext):
    await message.answer('Пожалуйста отправьте файл с разширением .zip')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp)
