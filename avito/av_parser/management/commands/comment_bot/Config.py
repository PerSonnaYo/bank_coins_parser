import logging
import vk
from aiogram import Bot
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.__count = settings.UPLOAD_LIMIT
        self.__vk_api, self.__vk_group, self.__tg_bot = self._parse_config()

    def _parse_config(self):
        vk_access_token = settings.VK_TOKEN
        session = vk.Session(access_token=vk_access_token)
        vk_api = vk.API(session, v='5.102')  # подключаем вк
        vk_group = settings.VK_GROUP_INFO
        telegram_bot_token = settings.TELEGA_TOKEN_BOT
        tg_bot = Bot(token=telegram_bot_token)  # подключаем телегу
        return vk_api, vk_group, tg_bot

    @property
    def Tbot(self):
        return self.__tg_bot

    @property
    def Vcount(self):
        return self.__count

    @property
    def Vapi(self):
        return self.__vk_api

    @property
    def Vgroup(self):
        return self.__vk_group
