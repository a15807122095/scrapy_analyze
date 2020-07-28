# -*-coding:utf-8-*-
import json
import requests
from common_tool import get_response, api_check, \
    check_local, API_return_600, API_return_200, post_response
from import_data_to_mysql import con_db
from datetime import datetime
from setting import db_setting


"""
英雄联盟其他赛区赛程 (过多延时已废弃)
从score网站上抓取 # https://www.scoregg.com/
"""

tournamentID = {
    '170': '2020 LCS夏季赛',
    '172': '2020 LPL夏季赛',
    '174': '2020 LDL夏季赛',
    '171': '2020 LEC夏季赛'
}

start_url = 'https://www.scoregg.com/services/api_url.php'
headers = {
# 'authority': 'www.scoregg.com',
# 'method': 'POST',
# 'path': '/services/api_url.php',
# 'scheme': 'https',
# 'accept': 'application/json, text/javascript, */*; q=0.01',
# 'accept-encoding': 'gzip, deflate, br',
# 'accept-language': 'zh-CN,zh;q=0.9',
# 'content-length': '113',
# 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
# 'cookie': 'Hm_lvt_7d06c05f2674b5f5fffa6500f4e9da89=1593337018,1593394093; PHPSESSID=vsj6t9q1h93ea6ugqgv5ub1is2; Hm_lpvt_7d06c05f2674b5f5fffa6500f4e9da89=1593396510',
# 'origin': 'https://www.scoregg.com',
# 'referer': 'https://www.scoregg.com/schedule',
# "sec-fetch-dest": "empty",
# "sec-fetch-mode": "cors",
# "sec-fetch-site": "same-origin",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
# "x-requested-with": "XMLHttpRequest"
}

form_data = {
'api_path': 'services/match/web_math_list.php',
'gameID': '1',
'date': '',
'tournament_id': '',
'api_version': '9.9.9',
'platform': 'web'
}


def parse(url, data, headers):
    types = 1
    game_name = '英雄联盟'
    source_from = 'score' # 爬虫网站源
    results = post_response(url, data, headers)
    results = results['data']['list']
    print(len(results), type(results), results)
    for key_list, result in results.items():
        match_list = result['info']
        for key, matchs in match_list.items():
            matchs = matchs['list']
            for match in matchs:
                league_sourcename = match['tournament_name']
                # 为避免与官网的冲突，先过滤掉LPL的赛程
                if 'LPL' not in league_sourcename:
                    team_a_sourcename = match['team_a_short_name']
                    team_b_sourcename = match['team_b_short_name']
                    status = match['status']
                    bo = match['game_count']
                    team_a_score = match['team_a_win']
                    team_b_score = match['team_b_win']
                    if team_a_score > team_b_score and status == '2':
                        win_team = 'A'
                    elif team_a_score < team_b_score and status == '2':
                        win_team = 'B'
                    else:
                        win_team = None
                    propertys = match['round_name']

                    start_time = match['start_date'] + ' ' + match['start_time'] + ':00'
                    check_match = league_sourcename + team_a_sourcename + team_b_sourcename + start_time
                    print('check_match:', check_match)

                    # 将字符串 start_date: "2020-06-29"与start_time: "04:00"拼接成 “2020-06-29 04:00:00”
                    # 再转换成赛程表中的10位时间戳字段
                    time_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M:00')
                    time_stamp = int(time_datetime.timestamp())
                    # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
                    status_check = check_local(db, check_match)
                    print('本地访问是否有记录：', status_check)
                    if status_check == None:
                        # 请求检测接口
                        result = api_check(game_name, league_sourcename, team_a_sourcename, team_b_sourcename)
                        print('检测接口返回：',result)
                        # 检测为600, result['result']包含6个字段：
                        # league_id, team_a_id, team_b_id,
                        # league_name, team_a_name, team_b_name
                        print('检测api结果：', result)
                        if result['code'] == 600:
                            insert_argument = {}
                            insert_argument['type'] = types
                            insert_argument['status'] = status
                            insert_argument['bo'] = bo
                            insert_argument['team_a_score'] = team_a_score
                            insert_argument['team_b_score'] = team_b_score
                            insert_argument['check_match'] = check_match
                            insert_argument['win_team'] = win_team
                            insert_argument['propertys'] = propertys
                            insert_argument['source_from'] = source_from
                            API_return_600(db, result, time_stamp, insert_argument)

                        elif result['code'] == 200:
                            # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                            API_return_200(db, result)
                            # 本地已有数据就直接更新
                    else:
                        print('本地已有数据就直接更新 ')
                        # 这里把check_match拿进去再更新一次没关系
                        db.update_by_id(types, status, bo, team_a_score, team_b_score, win_team, check_match,
                                        propertys, source_from, start_time, status_check)
                        print('本地已有数据就直接更新完成')




# 创建mysql连接对象
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])
parse(start_url, form_data, headers)