# -*-coding:utf-8-*-
import json
import requests
from common_tool import get_response, api_check, \
    check_local, API_return_600, API_return_200, post_response, get_weeks
from import_data_to_mysql import con_db
from datetime import datetime
from setting import headers_wzrygw


"""
英雄联盟其他赛区赛程 
从玩加网站上抓取 # https://www.wanplus.com/ajax/schedule/list
"""

start_url = 'https://www.wanplus.com/ajax/schedule/list'

headers= {
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
# last_weekstamp = int(monday_stamp - 86400)
# 下周1的00:00:00时间戳
next_weekstamp = int(monday_stamp + 86400 * 7)

time_list = [monday_stamp, next_weekstamp]




db = con_db()

def parse(url, data, db, headers):
    responses = post_response(url, data, headers)
    results = responses['data']['scheduleList']
    game_name = '英雄联盟'
    source_from = 'wanplus'  # 爬虫源网站
    types = 1
    for key_list, result in results.items():
        result = result['list']
        # print('赛程数据1:', type(result), result)
        for match in result:
            # print('赛程数据2:', type(match), match)
            league_sourcename = match['ename']
            # 只抓取LCK, LCS, LEC, LDL联赛
            if 'LCK' in league_sourcename or 'LCS' in league_sourcename or 'LEC' in league_sourcename or 'LDL' in league_sourcename :
                team_a_sourcename = match['oneseedname']
                team_b_sourcename = match['twoseedname']
                source_matchId = match['scheduleid']
                # 源数据中的start_time为‘17:00’类型，转换为时间戳再加上data中的‘time’才是表中的start_time类型
                time = match['starttime']
                strs = time.split(':')
                start_time = int(strs[0]) * 3600 + int(strs[1]) * 60 + data['time']
                start_time = str(start_time)
                # match['isover']表示是否结束， match['live']表示是否进行中
                if match['live']:
                    status = '1'
                elif not match['live'] and not match['isover']:
                    status = '0'
                else:
                    status = '2'
                bo = match['bonum']
                team_a_score = match['onewin']
                team_b_score = match['twowin']
                if team_a_score > team_b_score and status == '2':
                    win_team = 'A'
                elif team_a_score < team_b_score and status == '2':
                    win_team = 'B'
                else:
                    win_team = None
                propertys = match['groupname']


                # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
                check_match = league_sourcename + team_a_sourcename + team_b_sourcename + start_time
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



# # 上周的赛程
# print('开始抓上周赛程')
# form_data = {
#     '_gtk': 806653903,
#     'game': 2,
#     'time': last_weekstamp,
#     'eids': ''
# }
# parse(start_url, form_data, db, headers)
# print('上周赛程已抓取')

# 本周的赛程
# print('开始抓本周赛程')
form_data = {
    '_gtk': 806653903,
    'game': 2,
    'time': monday_stamp,
    'eids': ''
}
parse(start_url, form_data, db, headers)
# print('本周赛程已抓取')

# # 下周的赛程
# print('开始抓下周赛程')
form_data = {
    '_gtk': 806653903,
    'game': 2,
    'time': next_weekstamp,
    'eids': ''
}
parse(start_url, form_data, db, headers)
# print('下周赛程已抓取')