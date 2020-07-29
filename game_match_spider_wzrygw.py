# -*-coding:utf-8-*-
import json
from setting import db_setting
from common_tool import get_response, api_check, redis_return_operation, API_return_600, API_return_200
from import_data_to_redis import RedisCache_checkAPI
from import_data_to_mysql import con_db
import time
from datetime import datetime


"""
王者荣耀官网爬虫
"""

headers_wzry = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36'
}

redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

start_url = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage1.json'
def parse_wzry(url, db, headers):
    response = get_response(url, headers)
    sources = response['matchList']
    # print('抓取到的源数据：',len(sources), sources)
    game_name = '王者荣耀'
    source_from = '王者荣耀正赛官网'
    types = 2
    for source in sources:
        league_sourcename = source['cate'] + source['match_name']
        # cate可能也不是‘·’区分
        if '·' in source['cate']:
            cate = source['cate'].split('·')
            cate = cate[1]
        else:
            cate = source['cate']
        # print('名字：',cate)
        if cate == '常规赛':
            bo = '5'
        else:
            bo = 'Null'
        # 每个模块分一个或多个比赛
        propertys = cate
        source_lists = source['match']
        for source_list in source_lists:
            # status: (0:未进行, 1：进行中, 2：已完成)
            status = str(source_list['status'])
            source_matchId = source_list['matchid']
            # 没有获胜队伍字段,根据
            if int(source_list['wina']) > int(source_list['winb']) and status == '2':
                win_team = 'A'
            elif int(source_list['wina']) < int(source_list['winb']) and status == '2':
                win_team = 'B'
            else:
                win_team = None
            team_a_sourcename = source_list['teama_name']
            team_b_sourcename = source_list['teamb_name']
            if team_a_sourcename == '待定' or team_b_sourcename == '待定':
                continue
            team_a_score = source_list['wina']
            team_b_score = source_list['winb']
            # 官网的start_time格式为："2020-07-30 18:00"，要转化为时间戳
            start_time = source_list['mtime'] + ':00'
            start_time_date = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            start_time = start_time_date.timestamp()
            print('时间戳:', start_time)

            redis_return_operation(redis, game_name, db, source_from, league_sourcename, source_matchId, team_a_sourcename,
                    team_b_sourcename, start_time, types, team_a_score, team_b_score, status, bo, win_team, propertys)



parse_wzry(start_url, db, headers_wzry)

