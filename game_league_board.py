# -*-coding:utf-8-*-

import requests
import json
from common_tool import get_response, post_response, api_check_data
from datetime import datetime

"""
联赛积分榜（英雄联盟，王者荣耀在一张表）
抓取规则：
从start_url中post请求获取每个联赛的id
有联赛id拼接出常规赛，季后赛赛程 ：https://img1.famulei.com/tr/{联赛id}.json?_=1594797795974
从常规赛，季后赛赛程获取每周（小组）的id，拼接出这周（这组）比赛的赛果（过滤掉未进行的）
算出该赛程到目前为止，每个队伍的输赢数，净积分（小场赢一场积1分，输一场扣1分）
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

rank_url_pre = 'https://img1.famulei.com/tr/{0}.json?_={1}'

match_url_pre = 'https://img1.famulei.com/tr_round/{0}.json?_={1}'

team_win_count = {}
team_lose_count = {}
team_score_count = {}

def parse(form_data_yxlm, type):
    source = 'score'
    responses = post_response(start_url, form_data_yxlm, header)
    responses = responses['data']['list']
    # print('源数据：', responses)
    for response in responses:
        # 拿到联赛id
        tournamentID = response['tournamentID']
        source_league_name = response['short_name']
        # 13位时间戳
        now_time = datetime.now()
        timestamps = int(now_time.timestamp() * 1000)
        rank_url = rank_url_pre.format(tournamentID, timestamps)
        # print(rank_url, response)
        match_responses = get_response(rank_url, header)
        for match_response in match_responses:
            round_son = match_response['round_son']
            for match_list in round_son:
                id = match_list['id']
                # 拿到每周（每组）赛事列表的id
                # print('match_list的id:', id)
                # 怕根据时间戳反爬，在使用时间戳之前才生成时间戳
                now_time_match = datetime.now()
                timestamps_match = int(now_time_match.timestamp() * 1000)
                match_url = match_url_pre.format(id, timestamps_match)
                match_details = get_response(match_url, header)
                print('详情数据:', match_details)
                for match_detail in match_details:
                    team_a_name = match_detail['team_short_name_a']
                    team_b_name = match_detail['team_short_name_b']
                    print(111111, source_league_name, team_a_name, team_b_name)
                    # data_league = {'league_name':source_league_name, 'type':type}
                    # url_league = 'http://dev.saishikong.com/data/backstage-api/matching-league'
                    # data_response = requests.post(url=url_league, json=data_league)
                    # league_name = json.loads(data_response.text)
                    # print('联赛校验结果:', league_name)
                    # data_a_name = {'team_name':team_a_name, 'type':type}
                    # url_team = 'http://dev.saishikong.com/data/backstage-api/matching-team'
                    # data_response = requests.post(url=url_team, json=data_a_name)
                    # team_a_name = json.loads(data_response.text)
                    # print('a队校验结果:', team_a_name)
                    # data_b_name = {'team_name': team_b_name, 'type': type}
                    # data_response = requests.post(url=url_team, json=data_b_name)
                    # team_b_name = json.loads(data_response.text)
                    # print('b队校验结果:', team_b_name)


parse(form_data_yxlm, 1)
# print('英雄联盟抓取完成')
# parse(form_data_wzry, 2)
# print('王者荣耀抓取完成')


# https://img1.famulei.com/match/teamrank/152.json?_=1594781931989