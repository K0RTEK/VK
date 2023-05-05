import vk_api
import re
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime
import joblib
import psycopg2

with open('nothing.txt', 'r') as f:
    vk_api_key = f.readlines()

session = vk_api.VkApi(token=vk_api_key[0])

paste_group_id = input('Вставить ссылку на группу')
vk = session.get_api()
model = joblib.load('text_model.pkl')
conn = psycopg2.connect(dbname=vk_api_key[2], user=vk_api_key[3], password=vk_api_key[4], host=vk_api_key[5])

# Создаем курсор для выполнения запросов
cur = conn.cursor()


# получает Id по короткой ссылке вида public123123123
def getpublicid(group_url):
    return "public" + str(
        session.method("utils.resolveScreenName", {"screen_name": group_url[group_url.rfind("/") + 1::]})[
            'object_id'])


# получает Id по короткой ссылке интовым значением вида 123123123
def getid(group_url):
    return session.method("utils.resolveScreenName", {"screen_name": group_url[group_url.rfind("/") + 1::]})[
        'object_id']


# получает Id пользователей группы
def getgroupmembersid():
    not_closed_ids = [user_id for user_id in
                      session.method("groups.getMembers", {"group_id": getpublicid(paste_group_id)})['items'] if
                      vk.users.get(user_id=user_id, fields='is_closed')[0][
                          'is_closed'] is False]

    return not_closed_ids


async def get_group_members(group_id):
    url = 'https://api.vk.com/method/groups.getMembers'
    params = {
        'group_id': group_id,
        'v': '5.131',
        'access_token': vk_api_key,
        'fields': 'id'
    }
    async with aiohttp.ClientSession() as client:
        async with client.get(url, params=params) as resp:
            client_data = await resp.json()
            if 'response' in client_data:
                members = client_data['response']['items']
                ids = [member['id'] for member in members]
                return ids
            else:
                return []


async def get_all_group_members(group_ids):
    tasks = [get_group_members(group_id) for group_id in group_ids]
    results = await asyncio.gather(*tasks)
    return results


async def data():
    group_ids = [157180382]
    data_array = {}
    all_group_members = await get_all_group_members(group_ids)
    for group_members in all_group_members:
        for member_id in group_members:
            url = 'https://api.vk.com/method/users.get'
            params = {
                'user_id': member_id,
                'v': '5.131',
                'access_token': vk_api_key,
                'fields': 'is_closed'
            }
            async with aiohttp.ClientSession() as client_session:
                async with client_session.get(url, params=params) as resp:
                    client_session_data = await resp.json()
            if 'response' in client_session_data and client_session_data['response']:
                is_closed = client_session_data['response'][0]['is_closed']
                if not is_closed:
                    url = 'https://api.vk.com/method/groups.get'
                    params = {
                        'user_id': member_id,
                        'v': '5.131',
                        'access_token': vk_api_key,
                        'extended': 1,
                        'filter': 'groups',
                        'count': 1000
                    }
                    async with aiohttp.ClientSession() as client_session:
                        async with client_session.get(url, params=params) as resp:
                            client_session_data = await resp.json()
                    if 'response' in client_session_data:
                        groups = client_session_data['response']['items']
                        if 5 <= len(groups) <= 100:
                            g_ids = [group['id'] for group in groups]
                            data_array[member_id] = {key: value for key, value in
                                                     zip(g_ids, [get_group_posts(group['id'], 5) for group in groups if
                                                                 get_group_posts(group['id'], 1) is not None and (
                                                                     member_id, group) not in increment_insert()])}

        return data_array


def increment_insert():
    cur.execute("SELECT user_id, vk_group_id FROM user_vk_group")
    rows = cur.fetchall()
    return rows

    # получает id групп на которые подписан пользователь


def clean_text(text):
    # Удалить все вхождения "id12345" или "club12345" в тексте
    text = re.sub(r"(id|club)\d+", "", text)

    # Удалить все ссылки из текста
    pattern = r'https?://\S+|www\.\S+|\S+@\S+'

    text = re.sub(pattern, '', text)

    text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9]', ' ', text)

    text = " ".join(text.split())

    return text


def find_most_frequent_word(words):
    word_counts = {}
    for word in words:
        if word.isalpha():
            if word not in word_counts:
                word_counts[word] = 1
            else:
                word_counts[word] += 1
    try:
        most_frequent_word = max(word_counts, key=word_counts.get)
    except ValueError:
        return None
    return most_frequent_word


# получение постов с группы с условиями
def get_group_posts(id_group, amount):
    # Получаем 100 постов с группы(больше 100 не работает, даже после попыток обхода)
    try:

        response = vk.wall.get(owner_id='-' + str(id_group), count=amount, extended=1)
        posts = response['items']
        if response['count'] != 0:
            # выбор только не рекламных постов
            post_texts = [post['text'] for post in posts if not post.get('marked_as_ads')]
            post_texts = [clean_text(post) for post in post_texts if clean_text(post) != '']
            post_texts = [model.predict([text])[0] for text in post_texts]
            post_texts = find_most_frequent_word(post_texts)
            return post_texts
    except ValueError:
        pass


def get_user_posts(id_group):
    # Получаем 100 постов с группы(больше 100 не работает, даже после попыток обхода)

    response = vk.wall.get(owner_id=id_group, count=10, extended=1)
    posts = response['items']
    if response['count'] != 0:
        # выбор только не рекламных постов
        dates = [datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S') for post in posts]
        post_texts = [post['text'] for post in posts if not post.get('marked_as_ads')]
        post_texts = [clean_text(post) for post in post_texts if clean_text(post) != '']
        post_texts = [model.predict([text])[0] for text in post_texts]
        post_texts = [find_most_frequent_word(post_texts) for i in range(len(post_texts))]
        result = {key: value for key, value in zip(dates, post_texts)}
        return result
    else:
        return {'1970-01-01 00:00:00': 'Записи отсутствуют'}


# получение постов со всех групп из xlsx файла и присваивание им тегов.
# Сохранение данных в csv файл для обучения модели.
def save_data():
    df = pd.read_csv('train_data.csv')
    vk_groups = pd.read_excel('Книга 1.xlsx')
    # vk_api ругается если слишком часто получать id группы через ссылку
    # но отдельным генератором urls получить id групп можно(дебилизм)
    urls = [getid(url) for url in vk_groups['ссылка']]
    idx = 0
    for url in urls:
        for i in get_group_posts(url, 100):
            curr_data = {'text': i, 'tag': vk_groups['тематика'][idx]}
            df.loc[len(df)] = curr_data
        idx += 1
    df['text'] = list(map(clean_text, df['text']))
    df.to_csv('train_data.csv', index=False, lineterminator='', header=True)
    clean_data_test()


# не понятно почему удаление пропусков в датафрейме не работает в функции save_data(), но работает отдельно
# в этой функции, поэтому ее не трогать
def clean_data_test():
    df = pd.read_csv('train_data.csv')
    df = df.dropna()
    df.to_csv('train_data.csv', index=False, lineterminator='', header=True)


# функция сделана для пробных прогонов создания тренировочного файла с данными, потом ее надо будет удалить
def create_train_file():
    df = pd.DataFrame(columns=['text', 'tag'])
    # Сохранение DataFrame в CSV-файл
    df.to_csv('train_data.csv', index=False)
