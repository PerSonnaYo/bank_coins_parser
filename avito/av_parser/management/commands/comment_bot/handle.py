
def last_stack_first(comments, idx):
    'Возврат значений комментов в случае если их не больше двух'
    try:
        curr_price = int(comments['items'][idx]['text'])
        try:
            second_price = int(comments['items'][idx + 1]['text'])#если ставка + ставка или ставка + коммент
        except:
            second_price = 0 #если одна ставка
    except:
        try:#если коммент + ставка
            idx += 1
            curr_price = int(comments['items'][idx]['text'])
            second_price = 0
        except:
            curr_price = 100
            second_price = 0#если один коммент
    return curr_price, second_price

def last_stack_second(comments, idx):
    try:
        curr_price = int(comments['items'][idx]['text'])
    except:
        try:
            idx += 1
            curr_price = int(comments['items'][idx]['text'])
        except:
            idx += 1
            curr_price = int(comments['items'][idx]['text'])
    try:
        second_price = int(comments['items'][idx + 1]['text'])
    except:
        try:
            idx += 1
            second_price = int(comments['items'][idx + 2]['text'])
        except:
            idx += 1
            second_price = int(comments['items'][idx + 3]['text'])
    return curr_price, second_price

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