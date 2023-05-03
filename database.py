import psycopg2
from psycopg2 import sql
# from main import usersubscriptions

conn = psycopg2.connect(dbname='postgres', user='postgres', password='9181287qQq', host='localhost')


def users_subscriptions(values):
    with conn.cursor() as cursor:
        conn.autocommit=True
        insert = sql.SQL('insert into users_subscriptions (id, group_id) values {}').format(
            sql.SQL(',').join(map(sql.Literal, values)))
        cursor.execute(insert)


def getusersid():
    with conn.cursor() as cursor:
        cursor.execute('select id from users_subscriptions')
        column_names=[row[0] for row in cursor]
    return list(set(column_names))