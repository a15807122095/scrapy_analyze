# -*-coding:utf-8-*-
import json
import requests
from common_tool import get_response, api_check, check_local, API_return_600, API_return_200
from import_data_to_mysql import con_db
from lxml import etree
from datetime import datetime


"""
王者荣耀爬虫
url: https://pvp.qq.com/match/kcc.shtml
"""



header= {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}

# 选拔赛
url_choose1 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1592784000&end_time=1592870400&seasonid=KCC2020S'
url_choose2 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1592870400&end_time=1592956800&seasonid=KCC2020S'
url_choose3 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1593043200&end_time=1593129600&seasonid=KCC2020S'
url_choose4 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1593129600&end_time=1593216000&seasonid=KCC2020S'
url_choose5 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1593216000&end_time=1593302400&seasonid=KCC2020S'
url_choose6 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1593302400&end_time=1593388800&seasonid=KCC2020S'
urls_xuanba = [url_choose1, url_choose2, url_choose3, url_choose4, url_choose5, url_choose6]

# 小组赛
url_group1 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1594771200&end_time=1594857600&seasonid=KCC2020S'
url_group2 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1594857600&end_time=1594944000&seasonid=KCC2020S'
url_group3 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1594944000&end_time=1595030400&seasonid=KCC2020S'
url_group4 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595548800&end_time=1595635200&seasonid=KCC2020S'
url_group5 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595030400&end_time=1595116800&seasonid=KCC2020S'
url_group6 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595635200&end_time=1595721600&seasonid=KCC2020S'
url_group7 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595116800&end_time=1595203200&seasonid=KCC2020S'
url_group8 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595721600&end_time=1595808000&seasonid=KCC2020S'
url_group9 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595376000&end_time=1595462400&seasonid=KCC2020S'
url_groups = [url_group1, url_group2, url_group3, url_group4,
             url_group5, url_group6, url_group7, url_group8, url_group9]

# 淘汰赛
# url_knock =

def parse(url, headers, propertys, db):
    responses = get_response(url, headers)
    results = responses['data']
    # print(len(results), results)
    game_name = '王者荣耀'
    source_from = '王者荣耀官网'  # 爬虫源网站
    types = 2
    for result in results:
        # print('赛程数据1:', type(result), result)
        league_sourcename = result['season']
        team_a_sourcename = result['gname']
        team_b_sourcename = result['hname']
        # 源数据中的start_time为‘17:00’类型，转换为时间戳再加上data中的‘time’才是表中的start_time类型
        start_time = result['match_timestamp']
        # 官网的状态：1为未开赛， 2为已经开打  4为已打完（需要转化成表中的字段对应值）
        if result['match_state'] == 4:
            status = '2'
        elif result['match_state'] == 1:
            status = '0'
        else:
            status = '1'
        # print(result['match_state'], type(result['match_state']), status, result['guest_score'], type(result['guest_score']))
        # 官网没有bo数据，人工补充
        bo = 0
        team_a_score = result['guest_score']
        team_b_score = result['host_score']
        source_matchId = result['scheduleid']
        if team_a_score > team_b_score and status == '2':
            win_team = 'A'
        elif team_a_score < team_b_score and status == '2':
            win_team = 'B'
        else:
            win_team = None

        # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
        check_match = league_sourcename + team_a_sourcename + team_b_sourcename + start_time
        status_check = check_local(db, check_match)
        if status_check == None:
            # 请求检测接口
            result = api_check(game_name, league_sourcename, team_a_sourcename, team_b_sourcename)
            # print('检测接口返回：', result)
            # 检测为600, result['result']包含6个字段：
            # league_id, team_a_id, team_b_id,
            # league_name, team_a_name, team_b_name
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
                insert_argument['source_matchId'] = source_matchId
                API_return_600(db, result, start_time, insert_argument)

            elif result['code'] == 200:
                # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                API_return_200(db, result)
        # 本地已有数据就直接更新
        else:
            # print('本地已有数据就直接更新 ')
            # 这里把check_match拿进去再更新一次没关系
            db.update_by_id(types, status, bo, team_a_score, team_b_score, win_team, check_match,
                            propertys, source_from, source_matchId, status_check)
            # print('本地已有数据就直接更新完成')


db = con_db()
for url in urls_xuanba:
    propertys = '选拔赛'
    parse(url, header, propertys, db)

for url in url_groups:
    propertys = '小组赛'
    parse(url, header, propertys, db)

# 淘汰赛出来之后在加