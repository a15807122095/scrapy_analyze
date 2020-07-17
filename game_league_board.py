# -*-coding:utf-8-*-

import requests
import json
from common_tool import get_response, post_response, redis_check_rank, api_check
from import_data_to_redis import RedisCache_checkAPI
from import_data_to_mysql import con_db
from setting import db_setting
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


source = 'score'

# 用于统计胜负场次，净胜积分
team_win_count = {}
team_lose_count = {}
team_score_count = {}

redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse(form_data_yxlm, types):
    game_name = '英雄联盟' if types ==1 else '王者荣耀'
    # responses = post_response(start_url, form_data_yxlm, header)
    # responses = responses['data']['list']
    # print('源数据：', responses)
    # for response in responses:
    #     # 拿到联赛id
    #     tournamentID = response['tournamentID']
    #     source_league_name = response['short_name']
    # 13位时间戳
    source_league_name = '2020 LCK夏季赛'
    tournamentID = '173'
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
            # print('详情数据:', match_details)
            for match_detail in match_details:
                status = match_detail['status']
                team_a_win = int(match_detail['team_a_win'])
                team_b_win = int(match_detail['team_b_win'])
                source_team_a_name = match_detail['team_short_name_a']
                source_team_b_name = match_detail['team_short_name_b']
                source_matchid = match_detail['matchID']
                # 只统计完成的赛事
                if status == '2':
                    # print('源网站的赛事数据：',status, type(status), source_league_name, source_team_a_name, team_a_win, source_team_b_name, team_b_win)
                    # 检测redis中是否存在网站源的联赛id
                    redis_value = redis_check_rank(redis, source, source_matchid)
                    # redis中不存在这场比赛，访问后端接口拿到对局信息(联赛id和战队id是分两个接口返回的)
                    # print('redis返回的数据:', redis_value)
                    if not redis_value:
                        # 访问后端接口拿到联赛和两个战队id
                        result = api_check(game_name, source_league_name, source_team_a_name, source_team_b_name)
                        print(result)
                        if result['code'] == 600:
                            result = result['result']
                            league_id = result['league_id']
                            league_name = result['league_name']
                            team_a_id = result['team_a_id']
                            team_a_name = result['team_a_name']
                            team_b_id = result['team_b_id']
                            team_b_name = result['team_b_name']


                            # 从字典中取出合计的值，然后遍历计算，没有找到对应队伍就预设为0
                            team_score_count[team_a_name] = 0 if team_score_count.get(team_a_name) == None else \
                                team_score_count.get(team_a_name)
                            team_score_count[team_b_name] = 0 if team_score_count.get(team_b_name) == None else \
                                team_score_count.get(team_b_name)
                            team_win_count[team_a_name] = 0 if team_win_count.get(team_a_name) == None \
                                else team_win_count.get(team_a_name)
                            team_win_count[team_b_name] = 0 if team_win_count.get(team_b_name) == None \
                                else team_win_count.get(team_b_name)
                            team_lose_count[team_a_name] = 0 if team_lose_count.get(team_a_name) == None \
                                else team_lose_count.get(team_a_name)
                            team_lose_count[team_b_name] = 0 if team_lose_count.get(team_b_name) == None \
                                else team_lose_count.get(team_b_name)
                            # 净胜分：小场赢一场+1，输一场-1
                            team_score_count[team_a_name] = team_score_count[team_a_name] + team_a_win - team_b_win
                            team_score_count[team_b_name] = team_score_count[team_b_name] + team_b_win - team_a_win
                            # print('净胜分：', team_score_count[team_a_name], team_score_count[team_b_name])
                            # team_win_count中保存着键值对：  ‘战队名’:胜场
                            # team_lose_count中保存着键值对： ‘战队名’:负场
                            if team_a_win > team_b_win:
                                team_win_count[team_a_name] = team_win_count.get(team_a_name) + 1
                                team_lose_count[team_b_name] = team_lose_count.get(team_b_name) + 1
                            else:
                                team_win_count[team_b_name] = team_win_count.get(team_b_name) + 1
                                team_lose_count[team_a_name] = team_lose_count.get(team_a_name) + 1
                            # print('计算的数据为：', team_a_name, team_a_win, team_b_name, team_b_win)
                            # print('胜', team_win_count, '负', team_lose_count, '净胜分', team_score_count)

                            # 更新或插入数据库
                            sql_rank = "INSERT INTO `game_league_board` (league_id, team_id, win_count, lost_count, " \
                            "score, type_name, stage, type)  VALUES('{0}', '{1}', {2}, {3}, {4}, '{5}', '{6}', {7})  " \
                                       "ON DUPLICATE KEY UPDATE " \
                            "league_id='{0}', team_id='{1}', win_count={2}, lost_count={3}, score={4}, type_name='{5}', " \
                            "stage='{6}', type={7};".format(league_id, team_id, win_count, lost_count, score, type_name, stage, types)







parse(form_data_yxlm, 1)
# print('英雄联盟抓取完成')
# parse(form_data_wzry, 2)
# print('王者荣耀抓取完成')


# https://img1.famulei.com/match/teamrank/152.json?_=1594781931989