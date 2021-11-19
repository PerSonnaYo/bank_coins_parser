
# from django.core.management.base import BaseCommand
# from telegram import Bot
# from telegram import Update
# from telegram.ext import CallbackContext
# from telegram.ext import Filters
# from telegram.ext import MessageHandler
# from telegram.ext import Updater
# from telegram.utils.request import Request
from django.conf import settings
from av_parser.models import Product
import telepot
from pprint import pprint

bot = telepot.Bot(settings.TOKEN)

response = bot.getUpdates()

pprint(response)
# class Telega:
#     def __init__(self):
#         self.telegramBot = telepot.Bot(settings.TOKEN)
#
#     def send_message(self, p):
#         self.telegramBot.sendMessage(177914540, p, parse_mode="Markdown")

# def log_errors(f):
#     def inner(*args, **kwargs):
#         try:
#             return f(*args, **kwargs)
#         except Exception as ex:
#             error_mesage = f'Произошла ошибка {ex}'
#             print(error_mesage)
#             raise ex
#     return inner
#
# # @log_errors
# def display_new_product(p):
#     bot = Bot(token=settings.TOKEN)
#     # for i in ids:
#     #
#     #     try:
#     #         if image != '':
#     #             bot.sendPhoto(i, photo=open('Path' + image.name, 'rb'),
#     #                           caption=m_message)
#     #         else:
#     bot.sendMessage(p)
#         # except:
#         #     pass
#
# @log_errors
# def do_echo(update: Update, context: CallbackContext):
#     chat_id = update.message.chat_id
#     text = update.message.text
#     p = Product.objects.filter(
#         title__contains = text,
#         ).all()
#     p = Product.objects.filter(
#         id=p[0].id
#     ).update(price="11110000")
#     reply_text = "Boss ID = {}\n\n{}\n\n".format(chat_id, text,)
#     update.message.reply_text(
#         text=reply_text,
#     )
# class Command(BaseCommand):
#     help = 'Telega+avito'
#
#     def handle(self, *args, **options):
#         request = Request(
#             connect_timeout=0.5,
#             read_timeout=1.0
#         )
#         bot = Bot(
#             request=request,
#             token=settings.TOKEN
#         )
#         updater = Updater(
#             bot=bot,
#             use_context=True,
#         )
#         message_handler = MessageHandler(Filters.text, do_echo)
#         updater.dispatcher.add_handler(message_handler)
#
#         updater.start_polling()
#         updater.idle()