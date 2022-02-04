
def last_and_second_stacks(comments, step):
    'Определяем первый и второй комент'
    lent = len(comments['items'])
    met = False
    met2 = False
    curr_price = 100
    comment_id = 0
    second_price = 50#если один коммент
    sec_comm = 0
    i = 0
    while i < lent:
        if not met:
            try:
                curr = comments['items'][i]['text']
                if curr.lower() == 'старт':
                    curr_price = 100
                else:
                    curr_price = int(comments['items'][i]['text'])
                    if curr_price % step != 0:
                        i += 1
                        continue
                comment_id = comments['items'][i]['id']
                met = True
            except:
                i += 1
        if not met2 and met:
            if i < lent - 1:
                i += 1
            else:
                break
            try:
                curr = comments['items'][i]['text']
                if curr.lower() == 'старт':
                    second_price = 50
                else:
                    second_price = int(comments['items'][i]['text'])
                    if second_price % step != 0:
                        i += 1
                        continue
                sec_comm = comments['items'][i]['id']
                met2 = True
            except:
                i += 1
        if met2 and met:
            break
    return curr_price, comment_id, second_price, sec_comm

def make_stack(API, post, curr_price, id):
    while True:
        try:
            comment_id = API.wall.createComment(
                owner_id=id,
                post_id=post,
                message=str(curr_price),
            )['comment_id']
            return comment_id
        except:
            continue

def get_stacks(API, post, id, comment_id=0):
    while True:
        try:
            comments = API.wall.getComments(
                owner_id=id,
                post_id=post,
                need_likes=0,
                count=6,
                sort='desc',
                comment_id=comment_id,
            )
            return comments
        except:
            continue

def get_postss(API, num, groups, Vc):
    while True:
        try:
            posts = API.wall.get(
                owner_id=num,  # номер группы
                domain=groups[num],  # домен группы
                filter='owner',
                count=Vc,  # количество возвращаемых постов
            )
            return posts
        except:
            continue