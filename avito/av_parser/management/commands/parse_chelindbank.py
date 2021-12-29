# import datetime
# from collections import namedtuple
# import bs4
from selenium import webdriver
from logging import getLogger
# import requests
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from av_parser.models import Product
# print_tuple = namedtuple('Block', 'title,price,currency,date,url')

logger = getLogger(__name__)
# class Block(print_tuple):
#     def __str__(self):
#         return f'{self.title}\t{self.price}\t{self.currency}\t{self.date}\t{self.url}'
class avito_parser:
    def __init__(self):
        self.path = r'C:\Users\flman\PycharmProjects\pythonProject\chromedriver.exe'
        self.driver = None
    def get_page(self, page: int = None):
        self.driver = webdriver.Chrome(executable_path=self.path)
        if self.driver is None:
            raise CommandError("bad path --- block")
        self.driver.get('https://www.chelindbank.ru/private/others/coins/')
        if self.driver is None or self.driver is []:
            raise CommandError("bad url --- block")
        return self.driver.find_elements_by_css_selector(
            ".coins-list__item.coins-item"
        )
    def parse_block(self, item):
        x = item.text.split('\n')
        name = x[0]
        year1 = int(name.split('- ')[1])
        if year1 < 70:
            year = int("20" + year1)
        else:
            year = int("19" + year1)
        metall = x[2]
        nominal = x[10]
        nb = x[12]
        price = x[15]
        city = 'Челябинск'
        bank = 'Челиндбанк'
        try:
            price = int(price)
            try:
                #TODO: Если номер есть и цена меньше то выводим на экран
                #добавить год
                p = Product.objects.get(nb=nb)
                if p.price >= price:
                    p.name = name
                    p.price = price
                    p.metall = metall
                    p.nominal = nominal
                    p.nb = nb
                    p.city = city
                    p.bank = bank
                    p.save()
            except Product.DoesNotExist:
                p = Product(
                    name = name,
                    price = price,
                    metall = metall,
                    nominal = nominal,
                    nb = nb,
                    city = city,
                    bank = bank,
                )
                p.save()
                logger.debug(f'product{p}')
        except:
            logger.error("Ошибка  в номере\n")
    def get_blocks(self):
        text = self.get_page(page=1)
        self.driver.set_page_load_timeout(0.5)
        if text is None or text is []:
            raise CommandError("bad css --- block")
        for item in text:
            self.parse_block(item=item)

# p = avito_parser()
# p.get_blocks()
class Command(BaseCommand):
    help = 'Парсинг Челиндбанка'

    def handle(self, *args, **options):
        p = avito_parser()
        p.get_blocks()