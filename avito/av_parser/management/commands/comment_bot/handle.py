
def last_stack_first(comments, idx):
    'Возврат значений комментов в случае если их не больше двух'
    try:
        curr_price = int(comments['items'][idx]['text'])
        comment_id = comments['items'][idx]['id']
        try:
            second_price = int(comments['items'][idx + 1]['text'])#если ставка + ставка или ставка + коммент
            sec_comm = comments['items'][idx + 1]['id']#коммент йд для второй ставки
        except:
            second_price = 0 #если одна ставка
            sec_comm = 0
    except:
        try:#если коммент + ставка
            idx += 1
            curr_price = int(comments['items'][idx]['text'])
            comment_id = comments['items'][idx]['id']
            second_price = 0
            sec_comm = 0
        except:
            curr_price = 100
            comment_id = 0
            second_price = 0#если один коммент
            sec_comm = 0
    return curr_price, second_price, comment_id, sec_comm

def last_stack_second(comments, idx):
    try:
        curr_price = int(comments['items'][idx]['text'])
        comment_id = comments['items'][idx]['id']
    except:
        try:
            idx += 1
            curr_price = int(comments['items'][idx]['text'])
            comment_id = comments['items'][idx]['id']
        except:
            idx += 1
            curr_price = int(comments['items'][idx]['text'])
            comment_id = comments['items'][idx]['id']
    try:
        second_price = int(comments['items'][idx + 1]['text'])
        sec_comm = comments['items'][idx + 1]['id']
    except:
        try:
            second_price = int(comments['items'][idx + 2]['text'])
            sec_comm = comments['items'][idx + 2]['id']
        except:
            second_price = int(comments['items'][idx + 3]['text'])
            sec_comm = comments['items'][idx + 3]['id']
    return curr_price, second_price, comment_id, sec_comm

def check_win(comments, idx):
    if comments['items'][idx + 1]['text'] == 'winner':
        return True
    return False

def make_stack(API, post, curr_price, id):
    comment_id = API.wall.createComment(
        owner_id=id,
        post_id=post,
        message=str(curr_price),
    )['comment_id']
    return comment_id

def get_stacks(API, post, id, comment_id=0):
    comments = API.wall.getComments(
        owner_id=id,
        post_id=post,
        need_likes=0,
        count=6,
        sort='desc',
        comment_id=comment_id,
    )
    return comments

def discover_last_stack(comments):
    idx = 0
    if len(comments['items']) == 0:
        curr_price = 100
        second_price = 0
        comment_id = 0
        comment_id1 = 0
    elif len(comments['items']) < 3:
        curr_price, second_price, comment_id, comment_id1 = last_stack_first(comments, idx)
    else:
        curr_price, second_price, comment_id, comment_id1 = last_stack_second(comments, idx)
    return curr_price, second_price, comment_id, comment_id1