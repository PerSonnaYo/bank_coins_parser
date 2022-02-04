from asgiref.sync import sync_to_async
from logging import getLogger
from django.core.management.base import CommandError
from av_parser.models import Comments
from django.db.models import Q
import time as t
from . import handle as ha
from datetime import datetime
import pytz
from datetime import time
from django.conf import settings
from av_parser.models import Salers
import telepot

logger = getLogger(__name__)
bot = telepot.Bot(settings.TOKEN)

ONSALE = True
STOP = False
COUNTER = 0

@sync_to_async
def sql_block(url_lot, dated = None, url_saler = None, status = None,
              stack = None, name_saler = None, post_price = None,
              curr_price = None, comment_id = None, buy = None, my_current_price = None):
    global ONSALE
    try:
        p = Comments.objects.get(url_lot=url_lot)
        ONSALE = False
        if dated is not None:
            p.dated = dated
        if url_saler is not None:
            p.url_saler = url_saler
        if status is not None:
            p.status = status
        if stack is not None:
            p.stack = stack
        if name_saler is not None:
            p.name_saler = name_saler
        if post_price is not None:
            p.post1_price = post_price
        if curr_price is not None:
            p.current_price = curr_price
        if comment_id is not None:
            p.comment_id = comment_id
        if buy is not None:
            p.buy = buy
        if my_current_price is not None:
            p.my_current_price = my_current_price
        p.save()
        logger.debug(f'upgrade product{p}')
    except Comments.DoesNotExist:
        ONSALE = True
        p = Comments(url_lot=url_lot)
        if dated is not None:
            p.dated = dated
        if url_saler is not None:
            p.url_saler = url_saler
        if status is not None:
            p.status = status
        if stack is not None:
            p.stack = stack
        if name_saler is not None:
            p.name_saler = name_saler
        if post_price is not None:
            p.post1_price = post_price
        if curr_price is not None:
            p.current_price = curr_price
        if comment_id is not None:
            p.comment_id = comment_id
        if buy is not None:
            p.buy = buy
        if my_current_price is not None:
            p.my_current_price = my_current_price
        p.save()
        logger.debug(f'add product{p}')

def delete_sql_buffer():
    try:
        Comments.objects.all().delete()
        logger.info(f'|Comments| clear\n')
    except:
        logger.error(f'|BUFFER| error during clear')
        raise CommandError("bd is locked")

@sync_to_async
def ret_count():
    # entries = Entry.objects.filter(Q(entryType__icontains='МРТ') | Q(entryType__icontains='МСКТ'))
    return Comments.objects.filter(Q(status='proccess') | Q(status='---')).count()

@sync_to_async
def delete_lot():
    items = list(Comments.objects.filter(status='DELETED'))
    for item in items:
        item.delete()

@sync_to_async
def ret_list(API, step):
    #TODO upgrade
    global COUNTER
    global STOP
    count = Comments.objects.filter(Q(status='proccess') | Q(status='---')).count()
    while(count > 0):
        # time.sleep(5)
        items = Comments.objects.filter(Q(status='proccess') | Q(status='---'))
        for item in items:
            t.sleep(5)
            logger.info(f'proccess')
            post = item.url_lot.split('_')
            id = post[0].split('-')
            id = f'-{id[1]}'#номер группы
            post = post[1]#номер поста

            comments = ha.get_stacks(API, post=post, id=id)#парсим последние ставки
            curr_price, comment_id, second_price, comment_id_second = ha.last_and_second_stacks(comments)
                #после ставки возвращаем коммент ид который будем добавлять к запросу
            if second_price >= curr_price:#если новая ставка меньше чем последняя ставка
                if curr_price == item.my_current_price:#если максимальная ставка моя
                    Comments.objects.filter(url_lot=item.url_lot).update(status="proccess")
                else:#если максимальная ставк не моя
                    if (curr_price < item.stack):#если можно сделать еще ставку
                        Comments.objects.filter(url_lot=item.url_lot).update(status="proccess",
                            comment_id= ha.make_stack(API, post, second_price + step, id),
                            current_price = second_price + step,
                            my_current_price = second_price + step
                        )
                    else:#если ставку уже не сделаешь
                        Comments.objects.filter(url_lot=item.url_lot).update(
                            status = '---',
                            current_price = second_price,
                            comment_id = comment_id_second#коммент йд последней ставки
                        )

            elif item.my_current_price == curr_price: #если ставка не перебита
                Comments.objects.filter(url_lot=item.url_lot).update(status = 'proccess')
            elif item.my_current_price < curr_price:#если надо сделать новую ставку
                if curr_price >= item.stack:#если ставку уже поздно делать
                    Comments.objects.filter(url_lot=item.url_lot).update(
                        status = '---',
                        current_price = curr_price,
                        comment_id = comment_id  # коммент йд последней ставки
                     )
                else:#делаем ставку
                    Comments.objects.filter(url_lot=item.url_lot).update(
                        comment_id = ha.make_stack(API, post, curr_price + step, id),
                        current_price = curr_price + step,
                        status = 'proccess',
                        my_current_price = curr_price + step
                    )
        if STOP:#остановка процессов обработки
            COUNTER += 1
            if COUNTER == 2:
                STOP = False
                COUNTER = 0
            break
        count = Comments.objects.filter(Q(status='proccess') | Q(status='---')).count()

@sync_to_async
def check_finish(API):
    global STOP
    global COUNTER
    while True:
        moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
        current_time = time(moscow_time.hour, moscow_time.minute)
        need_time = time(22, 0)
        logger.info(f'time_isnt_passing')
        if (current_time >= need_time):
            break
        t.sleep(30)
        if STOP:
            COUNTER += 1
            if COUNTER == 2:
                STOP = False
                COUNTER = 0
            return
    count = Comments.objects.filter(Q(status='proccess') | Q(status='---')).count()
    while(count > 0):
        logger.info(f'win_check')
        items = Comments.objects.filter(Q(status='proccess') | Q(status='---'))
        for item in items:
            t.sleep(5)
            post = item.url_lot.split('_')
            id = post[0].split('-')
            id = f'-{id[1]}'  # номер группы
            post = post[1]  # номер поста

            comments = ha.get_stacks(API, post=post, id=id, comment_id=item.comment_id)
            for com in comments['items']:
                if 'свяжитесь' in com['text'].lower() or 'владельцем' in com['text'].lower():
                    if item.status == 'proccess':
                        Comments.objects.filter(url_lot=item.url_lot).update(status = 'OK')
                        bot.sendMessage(settings.CHAT_ID, f'WIN: {item}')
                    else:
                        Comments.objects.filter(url_lot=item.url_lot).update(status = 'DEFEAT')
                    break
            item.save()
        if STOP:
            COUNTER += 1
            if COUNTER == 2:
                STOP = False
                COUNTER = 0
            break

def cancel_work():
    global STOP
    STOP = True

@sync_to_async
def add_in_black_list(name_saler):
    try:
        p = Salers.objects.get(name_saler=name_saler)
    except Salers.DoesNotExist:
        p = Salers(name_saler=name_saler)
        p.save()

@sync_to_async
def check_black_list(name_saler):
    try:
        p = Salers.objects.get(name_saler=name_saler)
        return True
    except Salers.DoesNotExist:
        return False