import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Message,\
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from .comment_bot.Config import Config as cnf
from .comment_bot import sql_block as SQL
from .comment_bot import pars_functions as pf
from .comment_bot import handle as ha
import vk
import re
import datetime
import asyncio
import time
from collections import OrderedDict as od
from av_parser.models import Comments
from logging import getLogger
from django.core.management.base import CommandError
from django.core.management.base import BaseCommand
from django.conf import settings
import threading

#TODO добавить сообщение о победе
#TODO автоматические сообщения после победы боту
#TODO сформировать таблицу ответов с суммой и затем выслать ответ с окончательной ценой для оплаты кроме почты в боте и продавцу
#TODO обрабатывать страт только со 100 рублей
#TODO добавить двойную клавиатуру
#TODO добавить telebot
conf = cnf()

logger = getLogger(__name__)

SLIP = False
STEP = 50

bot = conf.Tbot
API = conf.Vapi

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

last_elem = ""#последний элемент
# создаём форму и указываем поля
class Form(StatesGroup):
    # date = State()
    job = State()
    stack = State()
    two_stack = State()

# Начинаем наш диалог
@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    # await Form.date.set()
    await message.reply("Привет! Введите интервал дней (Пример : -1 или 1) Допустим сегодня 28 число, а лоты заканчиваются 29, значит ввести надо 1")

@dp.message_handler(commands=['dd'])
async def handle_start(message: Message):
    global STEP
    await SQL.delete_lot()

    await asyncio.gather(
        SQL.ret_list(API, STEP),
        SQL.check_finish(API, bot))

# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

    # await state.finish()
    SQL.cancel_work()
    await message.reply('ОК')

# Сюда приходит ответ с именем
@dp.message_handler(content_types=['text'])
async def date_start(message: Message):
    global SLIP
    global STEP
    index = 1
    hh = False
    dd = message.text
    today = datetime.date.today()
    try:
        find_date = (today + datetime.timedelta(days=int(dd))).strftime('%d.%m.%Y')
        dated = (today + datetime.timedelta(days=int(dd))).strftime('%Y-%m-%d')#получаем дату исходя из запроса
    except:
        logger.error(f'invalid number of days')
        return await bot.send_message(message.chat.id, "Введите НОРМАЛЬНыЙ интервал дней (пример: 4)")
    groups = conf.Vgroup#парсим список групп
    for i, num in enumerate(groups):
        if hh == True:
            break
        posts = ha.get_postss(API, num, groups, conf.Vcount)
        for post in posts['items']:

            #TODO потом убрать
            # if index == 4:
            #     hh = True
            #     break
            # print('A')
            SLIP = False
            toxt = post['text']
            match = pf.start_pars(toxt)#вычленяем дату
            if len(match) == 0:
                continue
            if match[0] != find_date:#если даты не соответсвуют
                continue

            url_post = f"{groups[num]}?w=wall{num}_{post['id']}"
            await SQL.sql_block(url_post, dated=dated, )
            if SQL.ONSALE == False:#проверка есть ли уже в таблице
                continue
            # print('B')
            curr_stack = ha.get_stacks(API, post=post['id'], id=num)#определяем последнюю ставку
            curr_stack, comment_id, _, _ = ha.last_and_second_stacks(curr_stack)

            post_price = pf.pars_post(toxt)#парсим почту

            urlname = pf.pre_pars_name(toxt)
            fio, saler = pf.pars_name(urlname, API)#парсим имя продавца

            STEP = pf.pars_step(toxt)#Шаг торгов
            # print(STEP)
            await SQL.sql_block(url_post, post_price=post_price, url_saler=saler, status='DELETED', name_saler=fio, curr_price=curr_stack, comment_id=comment_id)

            description = pf.pars_discription(toxt)#описание лота
            url_photo1, url_photo2 = pf.pars_photo(post)#парсинг фоток
            # print(url_post)
            await bot.send_message(message.chat.id, description)
            # отправляем фотки
            while True:
                try:
                    await bot.send_media_group(message.chat.id, [InputMediaPhoto(url_photo1), InputMediaPhoto(url_photo2)])  # Отсылаем сразу 2 фото
                    break
                except:
                    time.sleep(2)
                    continue
            menu_kb = pf.make_kb(url_post, fio)#формируем клавиатуру
            await Form.job.set()
            index += 1
            logger.debug(f'parsing for {url_post} finished')
            await bot.send_message(
                chat_id=message.chat.id,
                reply_markup=menu_kb,
                text=f"(Шаг:{str(STEP)})\n{post_price}\nПоследняя ставка:{curr_stack}\nПродавец: {fio}\n{url_post}\nВыбирете действие ?")
            while (SLIP == False):#ожидаем выбора
                await asyncio.sleep(1)
    await bot.send_message(message.chat.id, "Обработка закончилась")
    #начинаем делать ставки

# Указываем что сделать при нажатии на кнопку,
# в нашем случаи прислать другую клавиатуру
@dp.message_handler(lambda message: message.text not in ["Пропустить", "Ставка", "Изменить прошлую ставку", "В черный список"], state=Form.job)
async def comman_invalid(message: Message):
    logger.error(f'invalid command')
    return await message.reply("Не знаю такой команды. Укажи команду кнопкой на клавиатуре")

@dp.callback_query_handler(state=Form.job)
async def process_stack(call: CallbackQuery, state: FSMContext):
    ff = call.data
    sp = ff.split(" ")
    action = sp[0]
    url = sp[1]
    async with state.proxy() as data:
        data['job'] = url#формируем номер группы + номер поста
    global SLIP
    await bot.edit_message_text(call.message.text, message_id=call.message.message_id,
                                chat_id=call.message.chat.id)
    if action == 'skip':
        await bot.send_message(call.message.chat.id, "Пропуск")
        await state.finish()
        SLIP = True
    if action == "stac":
        # Сделать ставку
        await bot.send_message(call.message.chat.id, "Пожалуйста, укажите ставку.")
        await Form.next()
    if action == "stoc":
        # Сделать ставку
        await bot.send_message(call.message.chat.id, "Пожалуйста, укажите 2 ставки.")
        await Form.next()
        await Form.next()
    if action == "blac":
        # В черный список
        await bot.send_message(call.message.chat.id, "ЧС обновлен.")
        await SQL.add_in_black_list(url)
        await state.finish()

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.stack)
async def stack_invalid(message: Message):
    logger.error(f'invalid stack')
    return await message.reply("Напиши ставку или напиши /cancel")

@dp.message_handler(lambda message: int(message.text) % STEP, state=Form.stack)
async def stack_invalid1(message: Message):
    logger.error(f'invalid stack')
    return await message.reply("Напиши четкую ставку или напиши /cancel")

# Сохраняем ставку
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.stack)
async def stack(message: Message, state: FSMContext):
    global STEP
    global last_elem
    async with state.proxy() as data:
        data['stack'] = int(message.text)
    global SLIP
    last_elem = data['job']
    await SQL.sql_block(data['job'], stack=data['stack'], status='proccess') #создаем общую базу где потом будем делать ставки
    await message.reply("Добавлен лот")
    logger.debug(f'add {data["job"]} finished')
    await state.finish()
    SLIP = True

# @dp.callback_query_handler(lambda c: c.data == 'good')
# async def callback(message: Message):
#     await bot.send_message(
#     chat_id=message.from_user.id,
#     reply_markup=feel_good_kb,
#     text="отлично")

@dp.message_handler(state=Form.two_stack)
async def stack(message: Message, state: FSMContext):
    global last_elem
    global STEP
    try:
        async with state.proxy() as data:
            buf = message.text
            buf = buf.split(' ')
            data['two_stack'] = int(buf[1])
        await SQL.sql_block(last_elem, stack=int(buf[0]))
        if (int(buf[0]) % STEP != 0 or int(buf[1]) % STEP != 0):#ставка должна быть валидной по правилам аукциона
            logger.error(f'invalid stack')
            return await message.reply("Напиши НормальНую1 ставку(20000 4000)")
    except:
        logger.error(f'invalid stack')
        return await message.reply("Напиши НормальНую ставку(20000 4000)")
    global SLIP
    last_elem = data['job']
    await SQL.sql_block(data['job'], stack=data['two_stack'], status='proccess')
    await message.reply("Добавлен лот")
    logger.debug(f'add {data["job"]} finished')
    await state.finish()
    SLIP = True

class Command(BaseCommand):
    help = 'Парсинг Банков'

    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
