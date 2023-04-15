import vk_api
from datetime import datetime
from DataBase import getusersid

session = vk_api.VkApi(
    token="vk1.a.Cyq9AScrJvxUTFoq3CDc7_bqYO9l1N89ZDT7owEwWyvrqTIVtaqxxaMtX-Dt5A0kpkaV-mBH9AzaAxw4YbgBdsPk0qoW4nann1IYiz\
    IoXelK2F2cjMgadmmxz0iiTcz1oNvNWUpYubIm64vgH-JWdlp-CSiGBeukBg_WQOMUDv9bi6HNj5eZyw_zP5aNwYILpTOdWG47KnbSpMcuqQf1Bg")
# тут надо написать input(), я заебался каждый раз вставлять ссылку
group_id = "https://vk.com/rut.digital"


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
def getid():
    return session.method("utils.resolveScreenName", {"screen_name": group_id[group_id.rfind("/") + 1::]})[
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
    posts = session.method("wall.get", {"owner_id": -getid()})['items']
    # print(posts)
    for post in range(10):
        print(posts[post]['text'])


# тут надо сделать функцию определения темы по тексту, иначе будет слишком много дрочи
# потом присвоим тему к group_id в таблице posts_by_group и там будем кластеризовать пользователей
# с лайками пока хз, еще не разобрался
if __name__ == '__main__':
    getpoststext()