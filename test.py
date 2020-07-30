# -*-coding:utf-8-*-

# from datetime import datetime
# import math
#
# date1 = '2020-07-27 00:00:00'
# date2 = '2020-07-28 00:00:00'
#
# date1_data = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
# date2_data = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
#
# date1_stamp = int(date1_data.timestamp())
# date2_stamp = int(date2_data.timestamp())
#
# sql = 'select * from game_python_match where start_time > {} and start_time < {};'.format(date1_stamp, date2_stamp)
# print(sql)

from common_tool import api_check, league_check, team_check, player_check, hero_check

# result1 = api_check('英雄联盟', '2020 LPL夏季赛', 'WE', 'OMG')
# print(result1)
# #
# result2 = league_check('2020 季中杯挑战赛', 1)
# print(result2)
# result3 = team_check('WE', 1)
# print(result3)
# result4 = player_check('UZI', 1)
# print(result4)
# result5 = hero_check('不灭狂雷', 1)
# print(result5)

from datetime import datetime, timedelta

now_date = datetime.now()
now_stamp = int(now_date.timestamp())

cookie_detailmessage =  'UM_distinctid=172d9950ded60f-00916514fef24f-4353761-e1000-172d9950deea7b; ' \
                  'Hm_lvt_c95eb6bfdfb2628993e507a9f5e0ea01=1594349716,1594629849,1594689821,1594950270; ' \
                  'Hm_lpvt_c95eb6bfdfb2628993e507a9f5e0ea01={}; ' \
                  'CNZZDATA1278221275=1183247664-1592785074-%7C1594954362'.format(now_stamp)

detail_heades = {
'authority': 'www.shangniu.cn',
'method': 'GET',
'path': '/api/battle/lol/match/liveBattle?battleId=26806599103',
'scheme': 'https',
'accept': 'application/json, text/plain, */*',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9',
'cookie': cookie_detailmessage,
'ctype': 'pc',
'referer': 'https://www.shangniu.cn/lol/268065991.html',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'token':'',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}

from common_tool import get_weeks
result = get_weeks()
print(result)




