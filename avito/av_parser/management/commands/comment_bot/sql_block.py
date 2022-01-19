from asgiref.sync import sync_to_async
from logging import getLogger
from django.core.management.base import CommandError
from av_parser.models import Comments
from django.db.models import Q
import time
from . import handle as ha

logger = getLogger(__name__)

ONSALE = True

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
    count = Comments.objects.filter(status='proccess').count()
    while(count > 0):
        time.sleep(5)
        items = Comments.objects.filter(status='proccess')
        for item in items:
            # time.sleep(5)
            print('fgrgrgrgrg')
            post = item.url_lot.split('_')
            id = post[0].split('-')
            id = f'-{id[1]}'#номер группы
            post = post[1]#номер поста

            comments = ha.get_stacks(API, post=post, id=id)#парсим последние ставки
            curr_price, second_price, comment_id, comment_id_second = ha.discover_last_stack(comments)
                #после ставки возвращаем коммент ид который будем добавлять к запросу

            if second_price >= curr_price:#если новая ставка меньше чем последняя ставка
                if curr_price == item.my_current_price:#если максимальная ставка моя
                    item.status = 'proccess'
                else:#если максимальная ставк не моя
                    if (curr_price < item.stack):#если можно сделать еще ставку
                        item.comment_id = ha.make_stack(API, post, second_price + step, id)
                        item.current_price = second_price + step
                        item.my_current_price = second_price + step
                        item.status = 'proccess'
                    else:#если ставку уже не сделаешь
                        item.status = '---'
                        item.current_price = second_price
                        item.comment_id = comment_id_second#коммент йд последней ставки

            elif item.my_current_price == curr_price: #если ставка не перебита
                item.status = 'proccess'

            elif item.my_current_price < curr_price:#если надо сделать новую ставку
                if curr_price >= item.stack:#если ставку уже поздно делать
                    item.status = '---'
                    item.current_price = curr_price
                    item.comment_id = comment_id  # коммент йд последней ставки
                else:#делаем ставку
                    item.comment_id = ha.make_stack(API, post, curr_price + step, id)
                    item.current_price = curr_price + step
                    item.status = 'proccess'
                    item.my_current_price = curr_price + step
            item.save()
        count = Comments.objects.filter(status='proccess').count()

@sync_to_async
def check_finish(API):
    #TODO добавить время после 22 по мск
    count = Comments.objects.filter(Q(status='proccess') | Q(status='---')).count()
    while(count > 0):
        time.sleep(5)
        items = Comments.objects.filter(Q(status='proccess') | Q(status='---'))
        for item in items:
            post = item.url_lot.split('_')
            id = post[0].split('-')
            id = f'-{id[1]}'  # номер группы
            post = post[1]  # номер поста

            comments = ha.get_stacks(API, post=post, id=id, comment_id=item.comment_id)
            for com in comments['items']:
                if 'победитель' in com['text']:
                    if item.status == 'proccess':
                        item.status = 'OK'
                    else:
                        item.status = 'DEFEAT'
                    break
            item.save()