import logging
import vk
from aiogram.types import CallbackQuery, Message,\
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pars_name(urlname, API):
    if urlname[0][0] == 'h':  # если вставлена ссылка
        id = urlname[0].split('/')[-1]
        fio = API.users.get(user_ids=id)
        n = fio[0]["first_name"]
        f = fio[0]["last_name"]
        fio = n + ' ' + f
        saler = urlname[0]
    elif(urlname[0][0] == '['):
        bb = urlname[0].split('|')
        fio = bb[-1][:-2]
        saler = f"https://vk.com/{bb[0][1:]}"
    else:
        bb = urlname[0].split('https://vk.com/')
        fio = bb[0][:-2]
        saler = f"https://vk.com/{bb[-1]}"
    return (fio, saler)

def pars_discription(text):
    description = text.split('Описание:')[1]
    description = description.split('Антиснайпер:')[0]
    return description

def pars_photo(post):
    foto = post['attachments']
    url_photo1 = foto[0]['photo']['sizes'][8]['url']  # первое фото
    url_photo2 = foto[1]['photo']['sizes'][8]['url']  # второе фото
    return (url_photo1, url_photo2)

def make_kb(url_post):
    u1 = f'skip {url_post}'#до 64 символов
    u2 = f'stack {url_post}'
    u3 = f'can_stack {url_post}'
    menu_kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="Пропустить", callback_data=u1),
        InlineKeyboardButton(text="Ставка", callback_data=u2),
        InlineKeyboardButton(text="Изменить прошлую ставку", callback_data=u3)
    )
    return menu_kb

def pars_post(text):
    try:
        post_price = re.findall(r'стоимость пересылки: (.*?)\nОплата', text)[0]
    except:
        post_price = re.findall(r'стоимость пересылки: (.*?)', text)[0]
    return (post_price)