import logging
import vk
from aiogram.types import CallbackQuery, Message,\
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pars_name(urlname, API):
    if urlname[0] == 'h':  # если вставлена ссылка
        id = urlname.split('/')[-1]
        if id[-1] == ' ':
            id = id[:-1]
        fio = API.users.get(user_ids=id)
        n = fio[0]["first_name"]
        f = fio[0]["last_name"]
        fio = n + ' ' + f
        saler = urlname
    elif(urlname[0] == '['):
        bb = urlname.split('|')
        fio = bb[-1][:-2]
        saler = f"https://vk.com/{bb[0][1:]}"
    else:
        bb = urlname.split('https://vk.com/')
        fio = bb[0][:-2]
        saler = f"https://vk.com/{bb[-1]}"
    return (fio, saler)

def pars_discription(text):
    try:
        description = text.split('Описание:')[1]
        description = description.split('Антиснайпер:')[0]
        if not re.search(r'[^\W\d]', description):
            description = 'Coin'
    except:
        try:
            description = text.split('Лот:')[1]
            description = description.split('\n')[0]
            if not re.search(r'[^\W\d]', description):
                description = 'Coin'
        except:
            description = 'Coin'
    return description

def pars_photo(post):
    try:
        foto = post['attachments']
        url_photo1 = foto[0]['photo']['sizes'][8]['url']  # первое фото
        try:
            url_photo2 = foto[1]['photo']['sizes'][8]['url']  # второе фото
        except:
            url_photo2 = 'https://a.d-cd.net/K5QQNtmo-k-AYNo5jDMn0BfYcIQ-960.jpg'
    except:
        url_photo1 = 'https://a.d-cd.net/K5QQNtmo-k-AYNo5jDMn0BfYcIQ-960.jpg'
        url_photo2 = 'https://a.d-cd.net/K5QQNtmo-k-AYNo5jDMn0BfYcIQ-960.jpg'
    return (url_photo1, url_photo2)

def make_kb(url_post):
    u1 = f'skip {url_post}'#до 64 символов
    u2 = f'stac {url_post}'
    u3 = f'stoc {url_post}'
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
        try:
            post_price = re.findall(r'стоимость пересылки: (.*?)', text)[0]
            if post_price == '':
                post_price = re.findall(r'стоимость пересылки: (.*?)Оплата', text)[0]
        except:
            post_price = re.findall(r'\nПересыл (.*?)\n', text)[0]
    return (post_price)

def start_pars(text):
    match = re.findall(r'ОКОНЧАНИЕ: (\d+\.\d+\.\d+) года', text)  # вычленяем дату
    if len(match) == 0:
        match = re.findall(r'Окончание: (\d+\.\d+\.\d+) г', text)  # вычленяем дату
    return match

def pre_pars_name(text):
    match = re.findall(r': (.*?)\nСтарт', text)
    if len(match) == 0:
        match = re.findall(r':(.*?)\nСтарт', text)
    if len(match) == 0:
        first = text.split('Владелец: ')
        second = first[1].split('\n \nНачало')[0]
        third = second.split('\n')[1]
        if third == ' ':
            third = second.split('\n \n')[1][:-1]
        match = third

    else:
        match = match[0]
    return match

def pars_step(toxt):
    try:
        s = int(re.findall(r'Шаг: (\d+)', toxt)[0])  # Шаг торгов
    except:
        s = int(re.findall(r'Шаг - (\d+)', toxt)[0])  # Шаг торгов
    return s