# -*-coding:utf-8-*-
import json
import requests
import urllib3
from common_tool import api_check, check_local, API_return_600, API_return_200
from import_data_to_mysql import con_db
import time
from datetime import datetime
from setting import url_wzrygw, headers_wzrygw


"""
王者荣耀官网爬虫
"""
def parse(url):
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url=url, headers=headers_wzrygw, verify = False)
    response = response.text
    response = json.loads(response)
    sources = response['matchList']
    # print('抓取到的源数据：',len(sources), sources)
    game_name = '王者荣耀'
    type = 2
    for source in sources:
        league_sourcename = source['cate'] + source['match_name']
        # cate为 "2020春季赛·总决赛"格式, 常规赛bo5  季后赛和总决赛bo7
        cate = source['cate'].split('·')
        cate = cate[1]
        if cate == '常规赛':
            bo = '5'
        else:
            bo = '7'
        # 每个模块分一个或多个比赛
        source_lists = source['match']
        for source_list in source_lists:
            # status: (0:未进行, 1：进行中, 2：已完成)
            status = str(source_list['status'])
            # 没有获胜队伍字段,根据
            if int(source_list['wina']) > int(source_list['winb']) and status == '2':
                win_team = 'A'
            elif int(source_list['wina']) < int(source_list['winb']) and status == '2':
                win_team = 'B'
            else:
                win_team = None
            team_a_sourcename = source_list['teama_name']
            team_b_sourcename = source_list['teamb_name']
            team_a_score = source_list['wina']
            team_b_score = source_list['winb']
            start_time = source_list['mtime']
            # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
            check_match = league_sourcename + team_a_sourcename + team_b_sourcename + start_time
            status_check = check_local(db, check_match)
            if status_check == None:
                # 请求检测接口
                result = api_check(game_name, league_sourcename, team_a_sourcename, team_b_sourcename)
                # print('检测接口返回：', result)

                if result['code'] == 600:
                    insert_argument = {}
                    insert_argument['type'] = type
                    insert_argument['status'] = status
                    insert_argument['bo'] = bo
                    insert_argument['team_a_score'] = team_a_score
                    insert_argument['team_b_score'] = team_b_score
                    insert_argument['check_match'] = check_match
                    insert_argument['win_team'] = win_team
                    # 将爬取的字符串时间转化为datetime类型
                    date_time = datetime.strptime(source_list['mtime'], '%Y-%m-%d %H:%M')
                    # 转化为时间戳
                    date_timestamp = int(time.mktime(date_time.timetuple()))
                    API_return_600(db, result,  date_timestamp, insert_argument)
                elif result['code'] == 200:
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
    for url in url_wzrygw:
        # print('开始抓取比赛')
        parse(url)
        # print('抓取比赛已完成')


