# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from common_tool import api_check, check_local, API_return_600, API_return_200
from import_data_to_mysql import con_db
from setting import url_finishs, url_matching, url_unfinishs, headers_yxlmgw

"""
英雄联盟官网爬虫
"""

def parse(url, match_status):
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url=url, headers=headers_yxlmgw, verify = False)
    sources = response.text
    sources = json.loads(sources)

    # 没有进行的比赛不解析 （没有进行比赛status为'-1'）
    if sources['status'] != '-1':
        sources = sources['msg']['result']
        # print('爬取的源数据：',len(sources), sources)
        game_name = '英雄联盟'
        type = 1
        status = match_status
        for each_source in sources:
            bo = each_source['GameMode']
            team_a_score = each_source['ScoreA']
            team_b_score = each_source['ScoreB']
            if each_source['MatchWin'] == '1':
                win_team = 'A'
            elif each_source['MatchWin'] == '2':
                win_team = 'B'
            else:
                win_team = None
            # print('比分数据：',type, status, bo, team_a_score, team_b_score, win_team)
            league_sourcename = each_source['GameName'] + each_source['GameTypeName']
            # 匹配A，B的名字
            bMatchName = each_source['bMatchName']
            bMatchName = bMatchName.split('vs')
            team_a_sourcename = bMatchName[0].strip()
            team_b_sourcename = bMatchName[1].strip()
            start_time = each_source['MatchDate']
            # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
            check_match= league_sourcename + team_a_sourcename + team_b_sourcename + start_time
            status_check = check_local(db, check_match)
            if status_check == None:
                # 请求检测接口
                result = api_check(game_name, league_sourcename, team_a_sourcename, team_b_sourcename)
                # print('检测接口返回：',result)
                # 检测为600, result['result']包含6个字段：
                # league_id, team_a_id, team_b_id,
                # league_name, team_a_name, team_b_name
                if result['code'] == 600:
                    insert_argument = {}
                    type = 1
                    insert_argument['type'] = type
                    insert_argument['status'] = status
                    insert_argument['bo'] = bo
                    insert_argument['team_a_score'] = team_a_score
                    insert_argument['team_b_score'] = team_b_score
                    insert_argument['check_match'] = check_match
                    insert_argument['win_team'] = win_team
                    # 将爬取的字符串时间转化为datetime类型
                    date_time = datetime.strptime(each_source['MatchDate'], '%Y-%m-%d %H:%M:%S')
                    # 转化为时间戳
                    date_timestamp = int(time.mktime(date_time.timetuple()))
                    API_return_600(db, result, date_timestamp, insert_argument)

                elif result['code'] == 200:
                    # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                    API_return_200(db, result)
            # 本地已有数据就直接更新
            else:
                # print('本地已有数据就直接更新 ')
                # 这里把check_match拿进去再更新一次没关系
                db.update_by_id(type, status, bo, team_a_score, team_b_score, win_team, check_match, status_check)
                # print('本地已有数据就直接更新完成')










if __name__ == '__main__':
    # 创建mysql连接对象
    db = con_db()
    # 拿到时间戳
    date_time = time.time()
    now_time = str(round(date_time * 1000))


    # 0:未开始 1:进行中 2:已结束
    # print('开始抓取已完成比赛')
    for url_finish in url_finishs:
        url_finish += now_time
        parse(url=url_finish, match_status='2')

    # print('开始抓取进行中比赛')
    url_matching += now_time
    parse(url_matching, match_status='1')

    # print('开始抓取未进行比赛')
    for url_unfinish in url_unfinishs:
        url_unfinish += now_time
        parse(url_unfinish, match_status='0')




