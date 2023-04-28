import vk_api
from datetime import datetime
import re
import pandas as pd

session = vk_api.VkApi(
    token="vk1.a.Cyq9AScrJvxUTFoq3CDc7_bqYO9l1N89ZDT7owEwWyvrqTIVtaqxxaMtX-Dt5A0kpkaV-mBH9AzaAxw4YbgBdsPk0qoW4nann1IYiz\
    IoXelK2F2cjMgadmmxz0iiTcz1oNvNWUpYubIm64vgH-JWdlp-CSiGBeukBg_WQOMUDv9bi6HNj5eZyw_zP5aNwYILpTOdWG47KnbSpMcuqQf1Bg")
# тут надо написать input(), я заебался каждый раз вставлять ссылку
group_id = "https://vk.com/baneksbest"
vk = session.get_api()


def lead_time(func):
    def wrapper():
        print("Функция начала работу")
        start = datetime.now()
        func()
        print("Функция закончила работу со временем: ", datetime.now() - start)

    return wrapper


# получает Id по короткой ссылке вида public123123123
def getpublicid():
    return "public" + str(
        session.method("utils.resolveScreenName", {"screen_name": group_id[group_id.rfind("/") + 1::]})[
            'object_id'])


# получает Id по короткой ссылке интовым значением вида 123123123
def getid(group_url):
    return session.method("utils.resolveScreenName", {"screen_name": group_url[group_url.rfind("/") + 1::]})[
        'object_id']


# получает Id пользователей группы
def getgroupmembersid():
    return session.method("groups.getMembers", {"group_id": getpublicid()})['items']


# получает id групп на которые подписан пользователь
# @lead_time
def usersubscriptions():
    data_array = []
    for user_id in getgroupmembersid():
        try:
            groups = session.method("users.getSubscriptions", {"user_id": user_id})['groups']['items']
            for i in range(len(groups)):
                data_array.append((user_id, groups[i]))
        except Exception:
            pass
    return data_array


# получает 10 постов группы, я подумал, что 100 слишком дохуя
def getpoststext():
    posts = session.method("wall.get", {"owner_id": -getid()})
    # print(posts)

    return [post['text'] for post in posts['items']]


def get_group_posts(group_id):
    # Получаем все посты с группы
    response = vk.wall.get(owner_id='-' + str(group_id), count=100, extended=1)
    posts = response['items']
    # Если постов больше 100, получаем оставшиеся
    try:
        while len(posts) < 100:
            response = vk.wall.get(owner_id='-' + str(group_id), count=100, extended=1, offset=len(posts))
            posts.extend(response['items'])
    except:
        pass

    # Извлекаем только тексты постов и удаляем все символы кроме букв и цифр
    post_texts = [re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9]', ' ', post['text']) for post in posts]

    return post_texts


def remove_extra_spaces(s):
    # Заменяем множественные пробелы одним пробелом
    s = " ".join(s.split())
    return s


def save_data():
    df = pd.read_csv('train_data.csv', index_col=None)
    data = pd.read_excel('book_1.xlsx')
    urls = [getid(url) for url in data['ссылка']]
    idx = 0
    for url in urls:
        for i in get_group_posts(url):
            curr_data = {'text': i, 'tag': data['тематика'][idx]}
            df.loc[len(df)] = curr_data
        idx += 1
    df['text'] = list(map(remove_extra_spaces, df['text']))
    df = df.dropna(subset=['text'])
    df.to_csv('train_data.csv', index=False, lineterminator='', header=False)


# тут надо сделать функцию определения темы по тексту, иначе будет слишком много дрочи
# потом присвоим тему к group_id в таблице posts_by_group и там будем кластеризовать пользователей
# с лайками пока хз, еще не разобрался
if __name__ == '__main__':
    save_data()
    # df = pd.DataFrame(columns=['text', 'tag'])
    #
    # # Сохранение DataFrame в CSV-файл
    # df.to_csv('train_data.csv', index=False)