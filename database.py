import psycopg2
from main import usersubscriptions
from main import get_user_posts

# Устанавливаем соединение с базой данных
conn = psycopg2.connect(dbname='vk', user='postgres', password='9181287qQq', host='localhost')

# Создаем курсор для выполнения запросов
cur = conn.cursor()


def users_subscriptions():
    # Создаем SQL-запрос на добавление данных в таблицу
    user_vk_group = "INSERT INTO user_vk_group (user_id, vk_group_id) VALUES (%s, %s)"
    vk_group_id_topic = "INSERT INTO vk_group_id_topic (vk_group_id, topic_group) VALUES (%s, %s)"
    user_characteristic = "INSERT INTO user_vk_characteristic (user_id, user_posts_date,topic_user) VALUES (%s, %s, %s)"
    # Получаем данные из словаря
    data = usersubscriptions()
    for user_id, group_data in data.items():
        for group_id, group_topic in group_data.items():
            # Задаем значения для user_vk_group
            values_user = (user_id, group_id)

            # Задаем значения для vk_group_id_topic
            values_group = (group_id, group_topic)

            # Выполняем запрос на добавление данных в таблицу
            cur.execute(user_vk_group, values_user)
            cur.execute(vk_group_id_topic, values_group)

            # Фиксируем изменения в базе данных
            conn.commit()
        data_user = get_user_posts(user_id)
        for post_date, user_topic in data_user.items():
            values_user_page = (user_id, post_date, user_topic)
            cur.execute(user_characteristic, values_user_page)
            conn.commit()

    # Закрываем курсор и соединение
    cur.close()
    conn.close()


users_subscriptions()