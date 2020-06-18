# -*-coding:utf-8-*-
import json
import requests
from datetime import datetime, timedelta
from setting import headers_yxlmgw
from lxml import etree

"""
尚牛电竞网爬虫
"""

# 爬取规则： 拿到本周的startTime和endTime的时间戳组成访问赛程url,根据时间戳差值拿到上周的赛程url
# 过滤只保留LPL的赛程,拿到每个赛程的matchId,拼接得到对局详情url    https://www.shangniu.cn/live/lol/268063898
# 用xpath拿到对局详情url的battle_id,拼接对局详情数据的url        https://www.shangniu.cn/api/battle/lol/match/liveBattle?battleId=26806389801

# startTime为本周1的00:00:00   endTime为本周1的00:00:00
now_time = datetime.now()
# 判断今天星期几（周1到周日对应0到6）
judge_week = now_time.weekday()
print(now_time)
start = now_time - timedelta(days=(judge_week))
last = start + timedelta(days=7)
start_str = start.strftime('%Y-%m-%d 00:00:00')
last_str = last.strftime('%Y-%m-%d 00:00:00')
start_date = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
last_date = datetime.strptime(last_str, '%Y-%m-%d %H:%M:%S')
startTime = int(start_date.timestamp()) * 1000
lastTime = int(last_date.timestamp()) * 1000
print(startTime, lastTime)

# 拼接本周的赛程url
url_matchlist = 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime, lastTime)
# 一周的时间戳差值为604800000
startTime_l = startTime - 604800000
lastTime_l = lastTime - 604800000
# 上周的赛程url
url_matchlist_l= 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime_l, lastTime_l)

url_list = [url_matchlist, url_matchlist_l]

# def parse_detail(urls, headers):
#     for url_match in urls:
#         response_match =





# parse_detail(url_list, headers_yxlmgw)