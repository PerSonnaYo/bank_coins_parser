import datetime
# from collections import namedtuple
import bs4
from logging import getLogger
import requests
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
        self.session = requests.Session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.607 Yowser/2.5 Safari/537.36',
            'accept-language': 'ru',
        }
    def get_page(self, page: int = None):
        params = {
            # 'radius': 0,
            # 'user': 1,
            'q' : 'сочи',
            'f' : 'ASgBAgECAUQcmgEBRcaaDBR7ImZyb20iOjE1MDAsInRvIjowfQ',
        }
        if page and page > 1:
            params['p'] = page
        url = 'https://www.avito.ru/sankt-peterburg/kollektsionirovanie/monety-ASgBAgICAUQcmgE'
        r = self.session.get(url, params=params)
        r.raise_for_status()
        return r.text
    @staticmethod
    def parse_date(item: str):
        params = item.strip().split(' ')
        if len(params) == 3 and params[2] == 'назад':
            day, time, p = params
            day = int(day)
            if time[0] == 'ч':
                date = datetime.datetime.today()
            elif time[0] == 'д':
                date = datetime.datetime.today() - datetime.timedelta(days=day)
            elif time[0] == 'н':
                date = datetime.datetime.today() - datetime.timedelta(days=day * 7)
            else:
                logger.error("Ошибка  в дате\n")
                return
            date = str(date)
            u = date.split(" ")
            return u[0]
        elif len(params) == 3:
            day, month1, time = params
            day = int(day)
            month_mas = {
                'января': 1,
                'февраля': 2,
                'марта': 3,
                'апреля': 4,
                'мая': 5,
                'июня': 6,
                'июля': 7,
                'августа': 8,
                'сентября': 9,
                'октября': 10,
                'ноября': 11,
                'декабря': 12,
            }
            month = month_mas.get(month1)
            if not month:
                logger.error("Ошибка  в дате\n")
                return
            today = datetime.datetime.today()
            time = datetime.datetime.strptime(time, '%H:%M').time()
            return datetime.datetime(day=day, month=month, year=today.year, hour=time.hour, minute=time.minute)

    def parse_block(self, item):
        url_block = item.select_one('div.iva-item-titleStep-_CxvN')
        # print(url_block)
        href = url_block.select_one('a.link-link-MbQDP.link-design-default-_nSbv.title-root-j7cja.iva-item-title-_qCwt.title-listRedesign-XHq38.title-root_maxHeight-SXHes')
        href_url = None
        if href:
            href_url = href.get('href')
        # print(href_url)
        # print(href)
        title = None
        if href_url:
            url = 'https://www.avito.ru'+href_url
            title_block = href.select_one(
                'h3.title-root-j7cja.iva-item-title-_qCwt.title-listRedesign-XHq38.title-root_maxHeight-SXHes.text-text-LurtD.text-size-s-BxGpL.text-bold-SinUO')
            title = title_block.string.strip()
        else:
            url = None
        # print(href)
        price_block = item.select_one('span.price-price-BQkOZ')
        l = price_block.contents
        currency = l[0]
        currency = currency.attrs['content'].strip()
        price = l[1]
        price = price.attrs['content'].strip()
        time = item.select_one('div.date-text-VwmJG.text-text-LurtD.text-size-s-BxGpL.text-color-noaccent-P1Rfs')
        time = self.parse_date(time.text)
        # print(time)
        if title is not None:
            try:
                price = int(price)
                try:
                    p = Product.objects.get(url=url)
                    p.title = title
                    p.price = price
                    p.save()
                except Product.DoesNotExist:
                    p = Product(
                        url=url,
                        title=title,
                        price=price,
                    ).save()
                logger.debug(f'product{p}')
            except:
                x = 0
    def get_blocks(self):
        text = self.get_page(page=1)
        soup = bs4.BeautifulSoup(text, 'lxml')
        pagin = soup.select('div.pagination-root-Ntd_O')
        if pagin is not None:
            for p in pagin:
                lst = p.contents
                f = str(lst[-2])
                f = f[f.find('(') + 1:f.find(')')]
                f = int(f)
                for j in range(2, f + 2):
                    container = soup.select('div.iva-item-content-UnQQ4')
                    if container is None:
                        raise CommandError("bad product block")
                    # container = container.select('div.iva-item-root-Nj_hb.photo-slider-slider-_PvpN.iva-item-list-H_dpX.iva-item-redesign-nV4C4.iva-item-responsive-gIKjW.items-item-My3ih.items-listItem-Gd1jN.js-catalog-item-enum')
                    # container = container.select('div.iva-item-content-UnQQ4')
                    for item in container:
                        self.parse_block(item=item)
                    text = self.get_page(page=j)
                    soup = bs4.BeautifulSoup(text, 'lxml')
        else:
            container = soup.select('div.iva-item-content-UnQQ4')
            s = 0
            # container = container.select('div.iva-item-root-Nj_hb.photo-slider-slider-_PvpN.iva-item-list-H_dpX.iva-item-redesign-nV4C4.iva-item-responsive-gIKjW.items-item-My3ih.items-listItem-Gd1jN.js-catalog-item-enum')
            # container = container.select('div.iva-item-content-UnQQ4')
            for item in container:
                self.parse_block(item=item)

class Command(BaseCommand):
    help = 'Парсинг Авито'

    def handle(self, *args, **options):
        p = avito_parser()
        p.get_blocks()