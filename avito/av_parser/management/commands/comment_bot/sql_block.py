from asgiref.sync import sync_to_async
from logging import getLogger
from django.core.management.base import CommandError
from av_parser.models import Comments
from django.db.models import Q

logger = getLogger(__name__)

ONSALE = True

@sync_to_async
def sql_block(url_lot, dated = None, url_saler = None, status = None,
              stack = None, name_saler = None, post_price = None,
              curr_price = None, comment_id = None, buy = None):
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
def ret_list(param):
    return Comments.objects.filter(status=param)