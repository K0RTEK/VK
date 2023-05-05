import datetime

import psycopg2
from main import get_user_posts
import numpy as np
from main import data
import asyncio
import aiohttp

with open('nothing.txt','r') as f:
    vk_api_key=[line.rstrip() for line in f.readlines()]

# Устанавливаем соединение с базой данных
conn = psycopg2.connect(dbname=vk_api_key[2], user=vk_api_key[3], password=vk_api_key[4], host=vk_api_key[5])

# Создаем курсор для выполнения запросов
cur = conn.cursor()
user_vk_group = "INSERT INTO user_vk_group (user_id, vk_group_id) VALUES (%s, %s)"
vk_group_id_topic = "INSERT INTO vk_group_id_topic (vk_group_id, topic_group) VALUES (%s, %s)"
user_vk_characteristic = "INSERT INTO user_vk_characteristic (user_id, user_posts_date,topic_user) VALUES (%s, %s, %s)"


async def dato():
    return await data()


def users_subscriptions():
    # Получаем данные из словаря
    doto = asyncio.run(dato())
    for user_id, group_data in doto.items():
        for group_id, group_topic in group_data.items():
            # Задаем значения для user_vk_group

            values_user = (user_id, group_id)
            if values_user in user_vk_group_insert():
                pass
            else:
                # Выполняем запрос на добавление данных в таблицу
                cur.execute(user_vk_group, values_user)
                # Фиксируем изменения в базе данных
                conn.commit()
        for group_id, group_topic in group_data.items():
            # Задаем значения для vk_group_id_topic
            values_group = (group_id, group_topic)
            if vk_group_id_topic_insert(values_group[0]) is None:
                pass
            else:
                # Выполняем запрос на добавление данных в таблицу
                cur.execute(vk_group_id_topic, values_group)
                # Фиксируем изменения в базе данных
                conn.commit()
        data_user = get_user_posts(user_id)
        for post_date, user_topic in dict(data_user).items():
            if (user_id, post_date) in user_id_insert():
                pass
            else:
                values_user_page = (user_id, post_date, user_topic)
                cur.execute(user_vk_characteristic, values_user_page)
                conn.commit()

    # Закрываем курсор и соединение
    cur.close()
    conn.close()


def vk_group_id_topic_insert(group_id):
    cur.execute("SELECT vk_group_id FROM vk_group_id_topic")
    rows = cur.fetchall()
    values_array = [row[0] for row in rows]
    new_arr = np.sort(values_array)
    index = np.searchsorted(new_arr, group_id)
    if index != len(new_arr) and new_arr[index] == group_id:
        return None
    else:
        return 1


def user_id_insert():
    cur.execute("SELECT user_id, user_posts_date FROM user_vk_characteristic")
    rows = cur.fetchall()
    rows = [(row[0], row[1].strftime('%Y-%m-%d %H:%M:%S')) for row in rows]
    return rows


def user_vk_group_insert():
    cur.execute("SELECT user_id, vk_group_id FROM user_vk_group")
    rows = cur.fetchall()
    return rows

# user_id_insert()
users_subscriptions()
# user_vk_group_insert()
