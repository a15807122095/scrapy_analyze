# -*-coding:utf-8-*-

import requests
import json
from common_tool import get_response, post_response

"""
联赛积分榜
（英雄联盟，王者荣耀在一张表）
"""

start_url = 'https://www.scoregg.com/services/api_url.php'

header = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}
form_data_yxlm = {
    'api_path': '/services/match/web_tournament_group_list.php',
    'method': 'GET',
    'platform': 'web',
    'api_version': '9.9.9',
    'language_id': 1,
    'gameID': 1,
    'type': 'all',
    'page': 1,
    'limit': 18,
    'year':''
}

form_data_wzry = {
'api_path': '/services/match/web_tournament_group_list.php',
'method': 'GET',
'platform': 'web',
'api_version': '9.9.9',
'language_id': 1,
'gameID': 2,
'type': 'all',
'page': 1,
'limit': 18,
'year':''
}

def parse(form_data_yxlm):
    responses = post_response(start_url, form_data_yxlm, header)
    responses = responses['data']['list']
    print('源数据：', responses)
    for response in responses:
        print(response)

parse(form_data_yxlm)
print('英雄联盟抓取完成')
# parse(form_data_yxlm)
# print('王者荣耀抓取完成')


# https://img1.famulei.com/match/teamrank/152.json?_=1594781931989