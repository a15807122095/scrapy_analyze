# -*-coding:utf-8-*-
'''
使用单例模式创建redis 链接池
'''
import json
from lxml import etree
from datetime import datetime
from common_tool import get_response, player_check, hero_check, team_check
# -*-coding:utf-8-*-
import json
import requests
from datetime import datetime
from common_tool import post_response

# stamp = 1595502900
# datetime1 = datetime.fromtimestamp(stamp)
# print(datetime1)
#
# now_date = datetime.now()
# now_stamp = int(now_date.timestamp())
# print(now_stamp)

now_date = datetime.now()
now_stamp = int(now_date.timestamp())
# print(now_stamp)
cookie_message = 'UM_distinctid=172d9950ded60f-00916514fef24f-4353761-e1000-172d9950deea7b; ' \
                 'Hm_lvt_c95eb6bfdfb2628993e507a9f5e0ea01=1594349716,1594629849,1594689821,1594950270; ' \
                 'CNZZDATA1278221275=1183247664-1592785074-%7C1594948928; ' \
                 'Hm_lpvt_c95eb6bfdfb2628993e507a9f5e0ea01={}'.format(now_stamp)
headers = {
'authority': 'www.shangniu.cn',
'method': 'GET',
'path': '/api/battle/index/matchList?gameType=lol&startTime=1594569600000&endTime=1595174400000',
'scheme': 'https',
'accept': 'application/json, text/plain, */*',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9',
'cookie': cookie_message,
'ctype': 'pc',
'referer': 'https://www.shangniu.cn/live/lol',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'token':'',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}

# url_matchlist_yxlm = 'https://www.shangniu.cn/api/battle/index/matchList?gameType=lol&startTime=1594569600000&endTime=1595174400000'
#
#
# proxies = {'https':'39.90.169.174:4582'}
#
# response = requests.get(url=url_matchlist_yxlm, headers=headers, proxies=proxies, timeout=7)
# response_text = response.text
# response_json = json.loads(response_text)
# print(response_json)


# # 测试select_query的返回值
# from import_data_to_mysql import con_db
# from setting import db_setting
# db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])
# sql = 'select id from game_player_hero_stats where id = 10;'
# result = db.select_query(sql)
# print(len(result))



# 导入 logging 模块
import logging
import sys


# # 生成同等路径下名为example.log的文件，的将级别为debug以上的信息输出，规定log的输出格式
# logging.basicConfig(
#     filename='example.log',
#     stream=sys.stdout,
#     level=logging.DEBUG,
#     datefmt='%Y/%m/%d %H:%M:%S',
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
#
#
# # 添加 log 记录示例
# logging.critical('logging critical message.')
# logging.error('logging error message')
# logging.warning('logging warning message')
# logging.info('logging info message')
# logging.debug('logging debug message')


{'CW+189': 3, 'EMC+896': 1, '广州TTG.XQ+695': 1, 'QGhappy+690': 8, 'ROX+826': 1, 'VSG电子竞技俱乐部+117': 2, 'DYG+698': 1, 'RNG.M+649': 5, 'eStarPro+699': 7, 'LGD电子竞技俱乐部—KPL+656': 6, 'ESG+115': 2, 'Nova电子竞技俱乐部+110': 0, 'WE电竞俱乐部+885': 8, 'VG电竞俱乐部+192': 7}
{'CW+189': 7, 'EMC+896': 0, '广州TTG.XQ+695': 0, 'QGhappy+690': 4, 'ROX+826': 0, 'VSG电子竞技俱乐部+117': 8, 'DYG+698': 0, 'RNG.M+649': 5, 'eStarPro+699': 4, 'LGD电子竞技俱乐部—KPL+656': 5, 'ESG+115': 7, 'Nova电子竞技俱乐部+110': 9, 'WE电竞俱乐部+885': 1, 'VG电竞俱乐部+192': 2}
{'CW+189': -7, 'EMC+896': 4, '广州TTG.XQ+695': 1, 'QGhappy+690': 4, 'ROX+826': 3, 'VSG电子竞技俱乐部+117': -8, 'DYG+698': 1, 'RNG.M+649': 0, 'eStarPro+699': 3, 'LGD电子竞技俱乐部—KPL+656': 1, 'ESG+115': -5, 'Nova电子竞技俱乐部+110': -9, 'WE电竞俱乐部+885': 7, 'VG电竞俱乐部+192': 5}










