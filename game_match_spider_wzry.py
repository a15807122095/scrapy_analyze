# -*-coding:utf-8-*-
import json
import requests
from common_tool import get_response, redis_return_operation, get_log
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_checkAPI
from setting import db_setting


"""
王者荣耀爬虫
url: https://pvp.qq.com/match/kcc.shtml
"""



header_wzry= {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}

# # 选拔赛
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
url_group4 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595030400&end_time=1595116800&seasonid=KCC2020S'
url_group5 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595116800&end_time=1595203200&seasonid=KCC2020S'
url_group6 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595376000&end_time=1595462400&seasonid=KCC2020S'
url_group7 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595462400&end_time=1595548800&seasonid=KCC2020S'

url_group8 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595548800&end_time=1595635200&seasonid=KCC2020S'
url_group9 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595635200&end_time=1595721600&seasonid=KCC2020S'
url_group10 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1595721600&end_time=1595808000&seasonid=KCC2020S'
url_groups_wzry = [url_group1, url_group2, url_group3, url_group4,
             url_group5, url_group6, url_group7, url_group8, url_group9, url_group10]


# 淘汰赛
url_knockout1 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1596067200&end_time=1596153600&seasonid=KCC2020S'
url_knockout2 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1596153600&end_time=1596240000&seasonid=KCC2020S'
url_knockout3 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1596240000&end_time=1596326400&seasonid=KCC2020S'
url_knockout4 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1596326400&end_time=1596412800&seasonid=KCC2020S'
url_knockout5 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1596844800&end_time=1596931200&seasonid=KCC2020S'
url_knockout6 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1596931200&end_time=1597017600&seasonid=KCC2020S'
url_knockout7 = 'https://app.tga.qq.com/openapi/tgabank/getSchedules?appid=10005&sign=K8tjxlHDt7HHFSJTlxxZW4A%2BalA%3D&begin_time=1597536000&end_time=1597622400&seasonid=KCC2020S'

url_knockout_list = [url_knockout1, url_knockout2, url_knockout3, url_knockout4, url_knockout5, url_knockout6, url_knockout7]








match_wzry_log = get_log('match_wzry')
redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse_wzry(url, headers, propertys, db):
    try:
        responses = get_response(url, headers)
        results = responses['data']
        # print(len(results), results)
        game_name = '王者荣耀'
        source_from = '王者荣耀官网'  # 爬虫源网站
        types = 2
        for result in results:
            # print('赛程数据1:', type(result), result)
            league_sourcename = result['season']
            team_a_sourcename = result['hname']
            team_b_sourcename = result['gname']
            # 过滤掉待定的赛程
            if team_a_sourcename == '待定' or  team_b_sourcename == '待定':
                continue
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
            team_a_score = result['host_score']
            team_b_score = result['guest_score']
            source_matchId = result['scheduleid']
            if team_a_score > team_b_score and status == '2':
                win_team = 'A'
            elif team_a_score < team_b_score and status == '2':
                win_team = 'B'
            else:
                win_team = None

            redis_return_operation(redis, game_name, db, source_from, league_sourcename, source_matchId,
                           team_a_sourcename, team_b_sourcename, start_time, types, team_a_score, team_b_score, status,
                           bo, win_team, propertys)

    except Exception as e:
        match_wzry_log.error(e, exc_info=True)


# for url in urls_xuanba:
#     propertys = '选拔赛'
#     parse_wzry(url, header_wzry, propertys, db)
#
# for url in url_groups_wzry:
#     propertys = '小组赛'
#     parse_wzry(url, header_wzry, propertys, db)

for url in url_knockout_list:
    propertys = '淘汰赛'
    parse_wzry(url, header_wzry, propertys, db)
