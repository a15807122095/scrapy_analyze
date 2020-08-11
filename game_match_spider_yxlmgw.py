# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from import_data_to_mysql import con_db
from common_tool import get_response, redis_return_operation, get_log
from setting import db_setting
from import_data_to_redis import RedisCache_checkAPI

"""
英雄联盟官网爬虫
"""

team_list = ['RNG', 'ES', 'EDG', 'LGD', 'IG', 'BLG', 'TES', 'SN', 'WE',
            'OMG', 'DMO', 'LNG', 'JDG', 'FPX', 'RW', 'VG', 'V5']

#   英雄联盟官网的url  headers---> headers_yxlmgw
# 正常情况下赛程页面是 url_finish_1：显示2条已完成  url_matching：进行中（status为‘-1’就是没有进行中的比赛） url_unfinish： 未开始

#  url_finish_2, url_finish_3 ：包含一周内已完成的比赛
#  url_unfinish_2, url_unfinish_3 ：包含一周内已完成的比赛

url_finish_1 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11=&p12=&page=1&pagesize=2&_='
url_finish_2 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11={0}&p12=&page=1&pagesize=8&_='




url_finishs = [url_finish_1, url_finish_2]

url_matching = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=9999&_='

url_unfinish_1 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=10&_='
url_unfinish_2 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12={0}&page=1&pagesize=8&_='
url_unfinish_3 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12={0}&page=1&pagesize=8&_='

match_yxlmgw_log = get_log('match_yxlmgw')

headers_yxlmgw = {
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

redis = RedisCache_checkAPI()

def parse_yxlm(url, db, match_status, headers):
    try:
        sources = get_response(url, headers)
        # 没有进行的比赛不解析 （没有进行比赛status为'-1'）
        if sources['status'] != '-1':
            sources = sources['msg']['result']
            # print('爬取的源数据：',len(sources), sources)
            game_name = '英雄联盟'
            source_from = '英雄联盟官网'
            types = 1
            status = match_status
            match_id = 0
            for each_source in sources:
                # 将爬取的字符串时间转化为datetime类型
                date_time = datetime.strptime(each_source['MatchDate'], '%Y-%m-%d %H:%M:%S')
                # 转化为时间戳
                date_timestamp = int(time.mktime(date_time.timetuple()))
                # print('修改前：', status)
                # 如果官网赛程是进行中而时间没到比赛时间,就把状态调整为未进行
                now_time = datetime.now()
                now_time_stamp = now_time.timestamp()
                if status == '1' and now_time_stamp < date_timestamp:
                    status = '0'
                # print('修改后：',now_time_stamp, date_timestamp, status)
                source_matchId = each_source['bMatchId']
                # bo = each_source['GameMode']
                # 现在为季后赛,暂时定bo为5
                bo = 5
                team_a_score = each_source['ScoreA']
                team_b_score = each_source['ScoreB']
                # 校正状态与比分，异常就pass掉
                # if status == '2' and (int(team_a_score) + int(team_b_score)) != int(bo):
                #     continue
                if each_source['MatchWin'] == '1':
                    win_team = 'A'
                elif each_source['MatchWin'] == '2':
                    win_team = 'B'
                else:
                    win_team = None
                # print('比分数据：', status, bo, team_a_score, team_b_score, win_team)
                league_sourcename = each_source['GameName'] + each_source['GameTypeName']
                # 截取GameTypeName后三位作为联赛性质字段
                propertys = each_source['GameTypeName'][-3:]
                # 匹配A，B的名字
                bMatchName = each_source['bMatchName']
                if 'vs' not in bMatchName:
                    continue
                bMatchName = bMatchName.split('vs')
                team_a_sourcename = bMatchName[0].strip()
                team_b_sourcename = bMatchName[1].strip()
                start_time = each_source['MatchDate']
                if team_a_sourcename not in team_list or team_b_sourcename not in team_list:
                    continue
                # print(team_a_sourcename, team_b_sourcename)

                redis_return_operation(redis, game_name, db, source_from, league_sourcename, source_matchId,
                       team_a_sourcename, team_b_sourcename, date_timestamp, types, team_a_score, team_b_score, status, bo,
                       win_team, propertys)
                # 取最后一个source_matchId作为url中的参数
                match_id = source_matchId
            return match_id
    except Exception as e:
        match_yxlmgw_log.error(e, exc_info=True)


# 拿到时间戳
date_time = time.time()
now_time = str(round(date_time * 1000))
# 创建mysql连接对象
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])
"""
英雄联盟爬虫抓取
"""
# 0:未开始 1:进行中 2:已结束
# 已完成的抓两次
print('开始抓取已完成比赛')
url_finish_1 = url_finish_1 + now_time
match_id = parse_yxlm(url_finish_1, db, '2', headers_yxlmgw)
# 上周已完成的url中的matchid是以当页最后一场已完成的matchid
url_finish_2 = url_finish_2.format(match_id) + now_time
parse_yxlm(url_finish_2, db, '2', headers_yxlmgw)
print(url_finish_1, url_finish_2)
print('已完成比赛抓取完毕')

# 未进行的
print('开始抓取未进行比赛')
url_unfinish_1 = url_unfinish_1 + now_time
print(url_unfinish_1)
match_id = parse_yxlm(url_unfinish_1, db, '0', headers_yxlmgw)
# # # 下周未完成的url中的matchid是以当页最后一场未完成的matchid
# url_unfinish_2 = url_unfinish_2.format(match_id) + now_time
# print(url_unfinish_2)
# match_id = parse_yxlm(url_unfinish_2, db, '0', headers_yxlmgw)
# url_unfinish_3 = url_unfinish_3.format(match_id) + now_time
# print(url_unfinish_3)
# parse_yxlm(url_unfinish_3, db, '0', headers_yxlmgw)

print('未进行比赛抓取完毕')

print('开始抓取进行中比赛')
parse_yxlm(url_matching, db, '1', headers_yxlmgw)
print(url_matching)
print('进行中比赛抓取完毕')





