# -*-coding:utf-8-*-
import requests
from lxml import etree
import urllib3
import json
from API_check import api_check

# 雷竞技
url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'
#
headers = {
        'USER-AGENT':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)'
    }

requests.packages.urllib3.disable_warnings()
response = requests.get(url=url, headers = headers, verify = False)
# 源数据
source = response.text
source = json.loads(source)

# 提取所需数据,提供（游戏名称，主队名称，客队名称）请求接口获取参数
source_list = source['result']

for result in source_list:
    result_game_name = result['game_name']
    if result_game_name == '王者荣耀' or result_game_name == '英雄联盟':
        result_tournament_name = result['tournament_name']
        result_team_A = result['team'][0]['team_name'].strip()
        result_team_B = result['team'][1]['team_name'].strip()
        print(result_game_name, result_tournament_name, result_team_A, result_team_B)
        payload = {
                        'game_name': result_game_name,
                        'league_name':result_tournament_name,
                        'team_a_name':result_team_A,
                        'team_b_name':result_team_B,
                       }
        result = api_check(payload)
        print(result)


#



