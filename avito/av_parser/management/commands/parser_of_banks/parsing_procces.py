from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import requests
from logging import getLogger
from django.core.management.base import CommandError
from av_parser.models import Product
from av_parser.models import Buffer
import pandas as pd
import tabula
from abc import ABC, abstractmethod
import re
from os import remove
import zope.interface
from zope.interface import implementer
from django.conf import settings
import telepot

logger = getLogger(__name__)

#TODO: сделать lowercase , узнать чат ид , путь для гуглдрайва

CSS_SBER = ".kitt-col.cc-coin-card__info-col"

class IParser(zope.interface.Interface):
    body = zope.interface.Attribute(u'Структура парсера.')
    def get_page(page: int = None, url: str = None, bank=None, region: str = None, type: str = None):
        'Start connection'
    def sql_block(name, nominal, year, city, bank, nb, metall, price):
        'fill table'
    def get_blocks(page: int = None, url=None, city: str = None, bank: str = None, region: str = None, type: str = None):
        'Parsing blocks'
    def parse_block(item, city, bank):
        'fill arguments for table'
    def start():
        'Start proccess'

def pager(get_page):
    """
    Декоратор, определяющий исходную страницу
    """
    def wrapper(self, page: int = None, url: str = None, bank=None, region: str = None, type: str = None):
        if url is not None and (page is not None and page > 1):
            if bank == "Сбербанк":
                old = f'/1/'
                new = f'/{page}/'
            elif bank == "Уралсиб":
                old = f'?p=1'
                new = f'?p={page}'
            url = url.replace(old, new)
        return get_page(self, page=page, url=url, bank=bank, region=region, type=type)
    return wrapper

@implementer(IParser)
class ParsingProcces(ABC):
    """
    Основной класс, определяющий режим подключения к сайту
    """
    def __init__(self):
        self.path = r'C:\Users\flman\PycharmProjects\pythonProject\chromedriver.exe'
        self.driver = None
        self.session = requests.Session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.607 Yowser/2.5 Safari/537.36',
            'accept-language': 'ru',
            # 'cookie' : 'JSESSIONID=CAz-URQ-mAsSbYcZ9YYep620XcHoWiWnoOUPcovP.gateway-15-g8f4s; TS019fab19=013ade2899c0173a759a87e947f12e1bdad979eff298d05a04cb7d9c8fce0b71d7a4ea2d2307a18513a8ca3fff32b326bbc0d2c51022f223cf62e8abec1069a46b9502ef64f1b93318326e673f4e98dcea2d61984e9a5e745e32e70f332113a1abe1577dfee10366ed9651df6da9ed9cc3a1137a388c46c9d4cf69bb43315442c6a32f3b26ea6a7a8356a4ce692624e4b37704ad1b; BBTracking="Mw=="; anonymousUserId=9c40d42f-ede5-40fd-85d4-288cd36e9f58; _gcl_au=1.1.57428365.1636312732; _gid=GA1.2.153107018.1636312735; abc4e19df5455fc72f51575e0d5bd928=5b32f38cf18fc057492e741d72bbea3f; ___dmpkit___=65bf55f7-9bc0-4024-9f17-3422406e78d5; _fbp=fb.1.1636312739354.217500980; tmr_lvid=0239eaf26c3a82de72363932128fd16e; tmr_lvidTS=1636312740200; _ym_uid=1636312760881338076; _ym_d=1636312760; cf44ad4bdad05ee181f953b4c4e5e921=428d79c0bfe52643bcb68c7014c14d40; _ym_isad=2; top100_id=t1.3122244.1566574414.1636312760975; adtech_uid=83358778-8f32-4e1a-b595-cb6c24c56a9e:sberbank.ru; user-id_1.0.5_lr_lruid=pQ8AALkmiGELHIYfAaUaaQA=; sbrf.region_id=78; sbrf.region_manual=true; tmr_detect=1|1636312799803; last_visit=1636302005347::1636312805347; redirectPortal=retail; _dc_gtm_UA-21169438-1=1; tmr_reqNum=11; t1_sid_3122244=s1.802097365.1636312760976.1636313556740.1.17.17; BBXSRF=75c159f3-2070-4d2b-aea1-e4011a6b3b06; JSESSIONID=SR28qqUBzhOTlLWccJF8WqqYxs9cnp_eYKp-bN2U.portalserver-live-12-gzbzd; _ga_2TDLL4T53E=GS1.1.1636312731.1.1.1636313558.0; _ga=GA1.2.202081278.1636312735; sbrf.region_set=true; X-Session-ID=80d6cecbcfe8736db8b2ecfe38b0546b; TS011f2bf6=013ade289974cf2421598681092bd172b12f2cf5f98f04664888d0bf439dab2c414e93b95bc636113d96e938683d33cbf61e56aca724bfb0e2cec23604c9ade20131f92577f2ef91d12dbb040a4f3f11ddf4d241d45be9dfbdda02f5db2e4b2134506376466c882a4ae2709ec6b463dfb6e76436e854c4db388a92dbff4d72e9ff1fc007f3c123a72d95592d92f710f1d360bd57636512ab22c516f3bc8897462642472fdd1c1c19dd55970767fe084a83af078a572bb7e8c90e83afb9908e86189cea50da',
        }
        self.bot = telepot.Bot(settings.TOKEN)

    def _param_cookie(self, region=None):
        s1 = {'name': 'sbrf.region_id', 'value': f'{region}', 'domain': 'www.sberbank.ru', 'path': '/'}
        s2 = {'name': 'sbrf.region_manual', 'value': 'true', 'domain': 'www.sberbank.ru', 'path': '/'}
        ret = ".kitt-pagination__pages"
        res = CSS_SBER
        return ((s1, s2, ret, res))

    def _first_load(self, page, url):
        if (page == 1):
            options = Options()
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(executable_path=self.path, options=options)
            if self.driver is None:
                logger.error("Неправильный путь driver\n")
                raise CommandError("bad path --- block")
            self.driver.get(url)
            time.sleep(2)
            if self.driver is None or self.driver is []:
                logger.error("Неправильный путь driver\n")
                raise CommandError("bad url --- block")

    @pager
    def get_page(self, page: int = None, url: str = None, bank=None, region: str = None, type: str = None):
        """
        Устанавливаем соединение
        """
        if (type == "sil"):
            self._first_load(page, url)
            tup = self._param_cookie(region)
            if (tup[0] != None and tup[1] != None):
                self.driver.add_cookie(tup[0])
                self.driver.add_cookie(tup[1])
            self.driver.get(url)
            self.driver.set_page_load_timeout(0.5)
            if self.driver is None or self.driver is []:
                logger.error("Неправильный url\n")
                raise CommandError("bad url --- block")
            return self.driver.find_elements_by_css_selector(tup[2]), self.driver.find_elements_by_css_selector(tup[3])
        elif(type == "req"):
            r = self.session.get(
                url,
                timeout=(60,60),
                stream=True,
            )
            r.raise_for_status()
            return (r.text)

    @abstractmethod
    def get_blocks(self, page: int = None, url=None, city: str = None, bank: str = None, region: str = None, type: str = None):
        pass

    @abstractmethod
    def parse_block(self, item, city, bank):
        pass

    @abstractmethod
    def start(self):
        pass

    def sql_block(self, name, nominal, year, city, bank, nb, metall, price):
        try:
            price = int(price)
            nominal = int(nominal)
            year = int(year)
            try:
                #TODO: Если номер есть и цена меньше то выводим на экран
                p = Product.objects.get(nb=nb)
                if p.price > price:
                    p.name = name
                    p.price = price
                    p.metall = metall
                    p.nominal = nominal
                    p.nb = nb
                    p.city = city
                    p.bank = bank
                    p.year = year
                    p.save()
                    self.bot.sendMessage(settings.CHAT_ID, f'NEW: {p}')
            except Product.DoesNotExist:
                p = Product(
                    name = name,
                    price = price,
                    metall = metall,
                    nominal = nominal,
                    year = year,
                    nb = nb,
                    city = city,
                    bank = bank,
                )
                p.save()
                self.bot.sendMessage(settings.CHAT_ID, f'NEW: {p}')
                logger.debug(f'product{p}')
        except:
            logger.error("Ошибка  в номере\n")

    def buffer_sql_block(self, name, price):
        try:
            p = Buffer(
                    name=name,
                    price=price,
                )
            p.save()
            logger.debug(f'|BUFFER| product {p}')
        except:
            logger.error("Ошибка sql buffer\n")

    def delete_sql_buffer(self):
        try:
            Buffer.objects.all().delete()
            logger.info(f'|BUFFER| clear\n')
        except:
            logger.error(f'|BUFFER| error during clear')
            raise CommandError("bd is locked")

    def clear_from_selling(self):
        try:
            posts = Product.objects.all()
            for post in posts:
                try:
                    item = Buffer.objects.get(name=post.name, price=post.price)
                except Buffer.DoesNotExist:
                    logger.debug(f'|PRODUCT| product {post} deleted')
                    post.delete()
        except:
            logger.error("Ошибка sql product\n")
            raise CommandError("bd is locked")

#--------Подклассы банков-----------------0----------------------------

class Sberbank_pars(ParsingProcces):
    """
    Класс парсинга сбера
    """
    def _loop_block(self, text):
        if len(text) != 0:
            for ite in text:
                start = ite.text.split('\n')[0]
                end = int(ite.text.split('\n')[-1])
                return end
        return 1

    def _parse_subblock(self, text):
        soup = BeautifulSoup(text, 'lxml')
        items = soup.select('div.characteristic_value.col-md-5.offset-md-1')
        if len(items) != 0:
            logger.error("Неверный селектор(ЦБ)")
            raise CommandError("bad product block")
        nominal = items[0].text.split(' ')[0]
        metall = items[2].text.split(' ')[0]
        return (nominal, metall)

    def parse_block(self, item, city, bank):
        text = item.text.split('\n')
        name = text[2]
        price = re.findall(r'\d+', text[1])
        price = ''.join(price)
        self.buffer_sql_block(name, price)
        try:
            # Если название уже есть в таблице то не надо парсить
            p = Product.objects.get(name=name)
            logger.debug(f'product {p} exist')
            return 1
        except Product.DoesNotExist:
            logger.debug(f'New product {name}')
        except:
            logger.error("Ошибка  в номере\n")
        nb = text[0]
        year1 = name.split('-')[-1]
        year1 = int(year1.replace(' ', ''))
        if year1 < 70:
            year = int("20" + str(year1))
        else:
            year = int("19" + str(year1))
        url = f'https://cbr.ru/cash_circulation/memorable_coins/coins_base/ShowCoins/?cat_num={nb}'
        text = self.get_page(page=1, url=url, type='req', bank='bank')
        nominal, metall = self._parse_subblock(text)
        self.sql_block(nominal=nominal,
                       price=price,
                       nb=nb,
                       year=year,
                       name=name,
                       city=city,
                       bank=bank,
                       metall=metall,
                       )

    def get_blocks(self, page: int = None, url=None, city: str = None, bank: str = None, region: str = None,
                   type: str = None):
        nb_str, items = self.get_page(page=page, url=url, type=type, bank=bank, region=region)
        it = self._loop_block(nb_str)
        if len(items) == 0:
            logger.error("Неверный селектор(Сбербанк)")
            raise CommandError("bad product block")
        for i in range(it):
            if i != 0:
                nb_str, items = self.get_page(page=i + 1, url=url, type=type, bank=bank, region=region)
            # items = self.driver.find_elements_by_css_selector(CSS_SBER)
            for item in items:
                self.parse_block(item=item, city=city, bank=bank)

    def start(self):
        self.get_blocks(
            page=1,
            url="https://www.sberbank.ru/ru/person/investments/values/mon#/page/1/search?prmax=50000&met1&met2&met3&tem7&condition=1",
            city="Санкт-Петербург",
            bank="Сбербанк",
            region='78',
            type='sil',
        )
        self.get_blocks(
            page=1,
            url="https://www.sberbank.ru/ru/person/investments/values/mon#/page/1/search?prmax=50000&met1&met2&met3&tem7&condition=1",
            city="Казань",
            bank="Сбербанк",
            region='16',
            type='sil',
        )
        self.get_blocks(
            page=1,
            url="https://www.sberbank.ru/ru/person/investments/values/mon#/page/1/search?prmax=50000&met1&met2&met3&tem7&condition=1",
            city="Челябинск",
            bank="Сбербанк",
            region='74',
            type='sil',
        )
        self.driver.quit()

class Chelind_pars(ParsingProcces):
    """
    Класс парсинга Челиндбанка
    """

    def parse_block(self, item, city, bank):
        x = item.text.split('\n')
        items = []
        for it in x:
            if (it != '' and it != '\r'):
                items.append(it)
        name = items[0]
        year1 = int(name.split('-')[-1])
        if year1 < 70:
            year = int("20" + str(year1))
        else:
            year = int("19" + str(year1))
        metall = items[2]
        nominal = items[10]
        nb = items[12]
        price = re.findall(r'\d+', items[15])[0]
        self.buffer_sql_block(name, price)
        self.sql_block(nominal=nominal,
                       price=price,
                       nb=nb,
                       year=year,
                       name=name,
                       city=city,
                       bank=bank,
                       metall=metall,
                       )

    def get_blocks(self, page: int = None, url=None, city: str = None, bank: str = None, region: str = None,
                   type: str = None):
        text = self.get_page(page=page, url=url, type=type, bank=bank)
        soup = BeautifulSoup(text, 'lxml')
        items = soup.select('div.coins-list__item.coins-item')
        if len(items) == 0:
            logger.error("Неверный селектор (Челиндбанк")
            raise CommandError("bad product block")
        for item in items:
            self.parse_block(item=item, city=city, bank=bank)
        self.session.close()

    def start(self):
        self.get_blocks(
            url='https://www.chelindbank.ru/umbraco/Api/CoinsApi/GetCoins?quality=Proof, ProofLike&popupName=proof&fil=0&metalType=all&',
            city="Челябинск",
            bank="Челиндбанк",
            type='req',
        )

class Uralsib_pars(ParsingProcces):
    """
    Класс парсинга Уралсиба
    """
    def _loop_block(self, arr):
        if len(arr) != 0:
            s = arr[0].text
            f = s.find('>')
            w = s[:f - 1]
            i = len(w) - 1
            while w[i] != '\n':
                i -= 1
            if i != len(w) - 1:
                num = int(w[i:])
            else:
                num = int(w[i])
            return num
        return 1

    def _parse_subblock(self, text):
        soup = BeautifulSoup(text, 'lxml')
        item = soup.select('div.coin-contaiber-right')
        if len(item) == 0:
            logger.error("Неверный селектор (Уралсиб Суб)\n")
            raise CommandError("bad product block")
        item = item[0]
        item1 = item.select('li.coin-characteristic_item')
        if len(item1) == 0:
            logger.error("Неверный селектор(Уралсиб Суб)\n")
            raise CommandError("bad product block")
        val = item1[7]
        nb = val.contents[3].text.strip(' ').strip('\n')
        return nb

    def parse_block(self, item, city, bank):
        first = 'https://www.uralsib.ru'
        href = item.get('href')
        name = item.select_one('h2.card-prev_title').text.strip('\n')
        price = item.select_one('span.currency.currency_rub').text.strip('\n').strip('\t')
        price = price.replace(' ', '')
        self.buffer_sql_block(name, price)
        try:
            # Если название уже есть в таблице то не надо парсить
            p = Product.objects.get(name=name)
            logger.debug(f'product {p} exist')
            return 1
        except Product.DoesNotExist:
            logger.debug(f'New product {name}')
        except:
            logger.error("Ошибка  в номере\n")
        try:
            year = int(name.split('-')[-1])
        except:
            year = 222
        x3 = item.select('span.card-prev_property-val')
        nominal = x3[1].text
        metall = x3[0].contents[0].strip(',').strip(' ')
        url = first + href
        url = url.split('?')[0]
        two_block = self.get_page(page=1, url=url, type='req', bank='bank')
        nb = self._parse_subblock(two_block)
        self.sql_block(nominal=nominal,
                       price=price,
                       nb=nb,
                       year=year,
                       name=name,
                       city=city,
                       bank=bank,
                       metall=metall,
                       )

    def get_blocks(self, page: int = None, url=None, city: str = None, bank: str = None, region: str = None,
                   type: str = None):
        text = self.get_page(page=page, url=url, type=type, bank=bank)
        soup = BeautifulSoup(text, 'lxml')
        container = soup.select('ul.pagination-list')
        it = self._loop_block(container)
        for i in range(it):
            if i != 0:
                text = self.get_page(page=i + 1, url=url, type=type, bank=bank)
            soup = BeautifulSoup(text, 'lxml')
            cont = soup.select('a.card-prev_wrapper')
            if len(cont) == 0:
                logger.error("Неверный селектор(Уралсиб)\n")
                raise CommandError("bad product block")
            for item in cont:
                self.parse_block(item=item, city=city, bank=bank)

    def start(self):
        self.get_blocks(
            page=1,
            url='https://www.uralsib.ru/investments-and-insurance/ivestitsii/invest-money/?p=1%5C&set_filter=y&coinsFilter_1242_MIN=0&coinsFilter_1242_MAX=100000&coinsFilter_1422_2802230650=Y&coinsFilter_1362_2104355073=Y&coinsFilter_1202_175210561=Y',
            city="Казань",
            bank="Уралсиб",
            type='req',
        )
        self.get_blocks(
            page=1,
            url='https://www.uralsib.ru/investments-and-insurance/ivestitsii/invest-money/?p=1%5C&set_filter=y&coinsFilter_1242_MIN=0&coinsFilter_1242_MAX=100000&coinsFilter_1422_2802230650=Y&coinsFilter_1362_678182442=Y&coinsFilter_1202_175210561=Y',
            city="Санкт-Петербург",
            bank="Уралсиб",
            type='req',
        )
        self.get_blocks(
            page=1,
            url='https://www.uralsib.ru/investments-and-insurance/ivestitsii/invest-money/?p=1%5C&set_filter=y&coinsFilter_1242_MIN=0&coinsFilter_1242_MAX=100000&coinsFilter_1422_2802230650=Y&coinsFilter_1362_808545698=Y&coinsFilter_1202_175210561=Y',
            city="Челябинск",
            bank="Уралсиб",
            type='req',
        )
        self.session.close()
class Chelyabinvest_pars(ParsingProcces):
    """
    Класс парсинга Челябинвестбанка
    """

    def parse_block(self, item, city, bank):
        first = 'https://chelinvest.ru'
        href = item.select_one('a').attrs['href']
        href = first + href
        r = requests.get(href)
        r.raise_for_status()
        file = 'monets.pdf'
        with open(file, "wb") as code:
            code.write(r.content)
        tables = tabula.read_pdf(file, pages="all")
        df_single = pd.DataFrame()
        for i, table in enumerate(tables, start=1):
            df_single = pd.concat([df_single, table])
        metall = 'Серебро'
        for i, row in enumerate(df_single.itertuples()):
            if i > 1:
                year = row[2]
                nb = row[1]
                if (nb == 'Монеты из золота'):
                    metall = 'Золото'
                    continue
                elif(nb == 'Инвестиционные монеты'):
                    break
                name = row[3]
                nominal = re.findall(r'\d+', row[5])[0]
                price = row[8][:-3]
                price = price.replace(' ', '')
                self.buffer_sql_block(name, price)
                self.sql_block(nominal=nominal,
                                  price=price,
                                  nb=nb,
                                  year=year,
                                  name=name,
                                  city=city,
                                  bank=bank,
                                  metall=metall,
                               )
        remove(file)

    def get_blocks(self, page: int = None, url=None, city: str = None, bank: str = None, region: str = None,
                   type: str = None):
        text = self.get_page(page=page, url=url, type=type, bank=bank)
        soup = BeautifulSoup(text, 'lxml')
        items = soup.select('td.right')
        if len(items) == 0:
            logger.error("Неверный селектор (Челябинвест)")
            raise CommandError("bad product block")
        item = items[0]
        self.parse_block(item=item, city=city, bank=bank)
        self.session.close()

    def start(self):
        self.get_blocks(
            url="https://chelinvest.ru/citizen/dragmet/price/",
            city="Челябинск",
            bank="Челябинвест",
            type='req',
        )