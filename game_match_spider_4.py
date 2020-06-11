# -*-coding:utf-8-*-
import requests
from lxml import etree
import urllib3
import time
import datetime
import json
from API_check import api_check

# 尚牛电竞网
url = 'https://www.shangniu.cn/api/battle/index/dayMatchList?' \
      'gameType=lol&startTime=1591804800000&endTime=1591891200000&dateType=today'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

requests.packages.urllib3.disable_warnings()
response = requests.get(url = url, headers = headers , verify = False)
results = response.text
results = json.loads(results)

results = results['body']

for result in results:
    if result['gameType'] == 'lol':
        game_name = '英雄联盟'
        league_name = result['leagueName']
        team_a_name = result['teamAShortName']
        team_b_name = result['teamBShortName']
        print(game_name, league_name, team_a_name, team_b_name)
        payload = {
            'game_name': game_name,
            'league_name': league_name,
            'team_a_name': team_a_name,
            'team_b_name': team_b_name,
        }
        result = api_check(payload)
        print(result)

    elif result['gameType'] == 'wzry':
        game_name = '王者荣耀'
        league_name = result['leagueName']
        team_a_name = result['teamAShortName']
        team_b_name = result['teamBShortName']
        print(game_name, league_name, team_a_name, team_b_name)
        payload = {
            'game_name': game_name,
            'league_name': league_name,
            'team_a_name': team_a_name,
            'team_b_name': team_b_name,
        }
        result = api_check(payload)
        print(result)




