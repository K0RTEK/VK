import vk_api
import re
import pandas as pd
import joblib
from datetime import datetime
# from database import user_vk_characteristic_insert
import psycopg2
import numpy as np
import aiohttp
import asyncio

import asyncio
import aiohttp
from datetime import datetime


async def get_group_members(group_id):
    url = 'https://api.vk.com/method/groups.getMembers'
    params = {
        'group_id': group_id,
        'v': '5.131',
        'access_token': 'vk1.a.Cyq9AScrJvxUTFoq3CDc7_bqYO9l1N89ZDT7owEwWyvrqTIVtaqxxaMtX-Dt5A0kpkaV-mBH9AzaAxw4YbgBdsPk0qoW4nann1IYiz\
    IoXelK2F2cjMgadmmxz0iiTcz1oNvNWUpYubIm64vgH-JWdlp-CSiGBeukBg_WQOMUDv9bi6HNj5eZyw_zP5aNwYILpTOdWG47KnbSpMcuqQf1Bg',
        'fields': 'id'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if 'response' in data:
                members = data['response']['items']
                ids = [member['id'] for member in members]
                return ids
            else:
                return []


async def get_all_group_members(group_ids):
    tasks = [get_group_members(group_id) for group_id in group_ids]
    results = await asyncio.gather(*tasks)
    return results


async def main():
    group_ids = [157180382]
    all_group_members = await get_all_group_members(group_ids)
    for group_members in all_group_members:
        for member_id in group_members:
            url = 'https://api.vk.com/method/users.get'
            params = {
                'user_id': member_id,
                'v': '5.131',
                'access_token': 'vk1.a.Cyq9AScrJvxUTFoq3CDc7_bqYO9l1N89ZDT7owEwWyvrqTIVtaqxxaMtX-Dt5A0kpkaV-mBH9AzaAxw4YbgBdsPk0qoW4nann1IYiz\
            IoXelK2F2cjMgadmmxz0iiTcz1oNvNWUpYubIm64vgH-JWdlp-CSiGBeukBg_WQOMUDv9bi6HNj5eZyw_zP5aNwYILpTOdWG47KnbSpMcuqQf1Bg',
                'fields': 'is_closed'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
            if 'response' in data and data['response']:
                is_closed = data['response'][0]['is_closed']
                if not is_closed:
                    url = 'https://api.vk.com/method/groups.get'
                    params = {
                        'user_id': member_id,
                        'v': '5.131',
                        'access_token': 'vk1.a.Cyq9AScrJvxUTFoq3CDc7_bqYO9l1N89ZDT7owEwWyvrqTIVtaqxxaMtX-Dt5A0kpkaV-mBH9AzaAxw4YbgBdsPk0qoW4nann1IYiz\
                    IoXelK2F2cjMgadmmxz0iiTcz1oNvNWUpYubIm64vgH-JWdlp-CSiGBeukBg_WQOMUDv9bi6HNj5eZyw_zP5aNwYILpTOdWG47KnbSpMcuqQf1Bg',
                        'extended': 1,
                        'filter': 'groups',
                        'count': 1000
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params) as resp:
                            data = await resp.json()
                    if 'response' in data:
                        groups = data['response']['items']
                        if 5 <= len(groups) <= 100:
                            print(f"Member {member_id} subscribed to groups: {[group['id'] for group in groups]}")


if __name__ == '__main__':
    now = datetime.now()
    asyncio.run(main())
    print(now - datetime.now())
