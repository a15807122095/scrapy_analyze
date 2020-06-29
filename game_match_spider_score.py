# -*-coding:utf-8-*-
import json
import requests
from common_tool import get_response, api_check, \
    check_local, API_return_600, API_return_200, post_response, get_weeks
from lxml import etree
from datetime import datetime
from setting import headers_wzrygw


"""
英雄联盟其他赛区赛程
从score网站上抓取 # https://www.scoregg.com/
"""

tournamentID = {
    '170': '2020 LCS夏季赛',
    '172': '2020 LPL夏季赛',
    '174': '2020 LDL夏季赛',
    '171': '2020 LEC夏季赛'
}

start_url = 'https://www.scoregg.com/services/api_url.php'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/83.0.4103.116 Safari/537.36'}
form_data = {
'api_path': 'services/match/web_math_list.php',
'gameID': '1',
'date': '',
'tournament_id': '',
'api_version': '9.9.9',
'platform': 'web'
}

def parse(url, data, headers):
    results = post_response(url, data, headers)
    results = results['data']['list']
    week_str = get_weeks()
    # print(week_str)
    for key, result in results.items():
        match_list = result['info']
        # print('赛程list：', len(match_list), match_list)
        for key, value in match_list.items():
            match = value['tournamentinfo']






parse(start_url, form_data, headers)