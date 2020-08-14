# -*-coding:utf-8-*-
from common_tool import post_response, get_log, redis_return_operation
from db.import_data_to_redis import RedisCache_checkAPI
from db.import_data_to_mysql import con_db
from datetime import datetime
from setting import db_setting


"""
英雄联盟其他赛区赛程 
从玩加网站上抓取 # https://www.wanplus.com/ajax/schedule/list
"""

start_url_wanplus = 'https://www.wanplus.com/ajax/schedule/list'

headers_wanplus= {
'authority': 'www.wanplus.com',
'method': 'POST',
'path': '/ajax/schedule/list',
'scheme': 'https',
'accept': 'application/json, text/javascript, */*; q=0.01',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9',
'content-length': '43',
'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
'cookie': 'wanplus_token=f4f5aa3f18cc3119abe8cdabc5a7cebe; wanplus_storage=lf4m67eka3o; wanplus_sid=9e696f0029946fb2c4f9a8b7c523c370; UM_distinctid=172ff8aed371e-009aa63dd252d6-4353760-e1000-172ff8aed38670; wp_pvid=5917824012; gameType=2; wanplus_csrf=_csrf_tk_806653903; wp_info=ssid=s8611067605; Hm_lvt_f69cb5ec253c6012b2aa449fb925c1c2=1593425195,1593479359; isShown=1; CNZZDATA1275078652=1155513258-1593421357-%7C1593480701; Hm_lpvt_f69cb5ec253c6012b2aa449fb925c1c2=1593485299',
'origin': 'https://www.wanplus.com',
'referer': 'https://www.wanplus.com/lol/schedule',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
'x-csrf-token': '806653903',
'x-requested-with': 'XMLHttpRequest'
}

# 玩加网站的post参数主要拿time，上周为周日的00：00:00的时间戳，本周和下周为周1的00:00:00时间戳
# 应该是点击上周就以上周日00:00:00的时间戳为time，点击下周就以下周1的00:00:00的时间戳为time

today = datetime.now()
week_day = today.weekday()
today_str = today.strftime('%Y-%m-%d 00:00:00')
str_today = datetime.strptime(today_str, '%Y-%m-%d %H:%M:%S')
today_stamp = str_today.timestamp()
# 这周1的00:00:00时间戳
monday_stamp = int(today_stamp - 86400 * week_day)
# # 上周日的00:00:00时间戳
last_weekstamp = int(monday_stamp - 86400)
# 下周1的00:00:00时间戳
next_weekstamp = int(monday_stamp + 86400 * 7)

time_list = [monday_stamp, next_weekstamp]

match_wanplus_log = get_log('match_wanplus')

redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse_wanplus(url, data, db, headers):
    try:
        responses = post_response(url, data, headers)
        results = responses['data']['scheduleList']
        game_name = '英雄联盟'
        source_from = 'wanplus'  # 爬虫源网站
        types = 1
        for key_list, result in results.items():
            date_time = result['time']
            result = result['list']
            # 有的字段是bool类型，过滤掉
            if type(result) == bool:
                continue
            # print('赛程数据1:', key_list, type(result), result)
            for match in result:
                # print('赛程数据2:', key_list, type(match), match)
                league_sourcename = match['ename']
                # 只抓取LCK, LCS, LEC, LDL联赛
                if 'LCK' in league_sourcename or 'LCS' in league_sourcename or 'LEC' in league_sourcename or 'LDL' in league_sourcename:
                    team_a_sourcename = match['oneseedname']
                    team_b_sourcename = match['twoseedname']
                    source_matchId = match['scheduleid']
                    # 源数据中的start_time为‘17:00’类型，转换为时间戳再加上result['time']才是表中的start_time类型
                    time = match['starttime']
                    strs = time.split(':')
                    start_time = int(strs[0]) * 3600 + int(strs[1]) * 60 + date_time
                    start_time = str(start_time)

                    bo = match['bonum']
                    team_a_score = match['onewin']
                    team_b_score = match['twowin']

                    # match['isover']表示是否结束， match['live']表示是否进行中
                    # 同时也要用两队比分之和是否等于bo来判断是否结束
                    if match['live']:
                        status = '1'
                    elif not match['live'] and not match['isover']:
                        status = '0'
                    else:
                        # 判断两队的分值和是否为bo,网站有可能status为2但是没打完
                        if int(team_a_score) + int(team_b_score) >= (bo/2):
                            status = '2'
                        else:
                            status = '1'
                    if int(team_a_score) > int(team_b_score) and status == '2':
                        win_team = 'A'
                    elif int(team_a_score) < int(team_b_score) and status == '2':
                        win_team = 'B'
                    else:
                        win_team = None
                    propertys = match['groupname']

                    redis_return_operation(redis, game_name, db, source_from, league_sourcename, source_matchId,
                           team_a_sourcename, team_b_sourcename, start_time, types, team_a_score, team_b_score, status, bo,
                           win_team, propertys)
    except Exception as e:
        match_wanplus_log.error(e, exc_info=True)



## 上周的赛程
# print('开始抓上周赛程')
# form_data = {
#     '_gtk': 806653903,
#     'game': 2,
#     'time': last_weekstamp,
#     'eids': ''
# }
# parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
# print('上周赛程已抓取')

# 本周的赛程
# print('开始抓本周赛程')
form_data = {
    '_gtk': 121196025,
    'game': 2,
    'time': monday_stamp,
    'eids': ''
}
parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
# print('本周赛程已抓取')

# # 下周的赛程
# print('开始抓下周赛程')
form_data = {
    '_gtk': 121196025,
    'game': 2,
    'time': next_weekstamp,
    'eids': ''
}
parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
# print('下周赛程已抓取')

# def run_game_match_spider_wanplus():
#     ## 上周的赛程
#     # print('开始抓上周赛程')
#     # form_data = {
#     #     '_gtk': 806653903,
#     #     'game': 2,
#     #     'time': last_weekstamp,
#     #     'eids': ''
#     # }
#     # parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
#     # print('上周赛程已抓取')
#
#     # 本周的赛程
#     # print('开始抓本周赛程')
#     form_data = {
#         '_gtk': 121196025,
#         'game': 2,
#         'time': monday_stamp,
#         'eids': ''
#     }
#     parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
#     # print('本周赛程已抓取')
#
#     # # 下周的赛程
#     # print('开始抓下周赛程')
#     form_data = {
#         '_gtk': 121196025,
#         'game': 2,
#         'time': next_weekstamp,
#         'eids': ''
#     }
#     parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
#     # print('下周赛程已抓取')