# -*-coding:utf-8-*-
import json
import time
import re
import requests
from datetime import datetime, timedelta
from common_tool import get_response
from setting import headers_yxlmgw
from lxml import etree

"""
尚牛电竞网爬虫
"""

# LPL战队列表
LPL_list = [ 'RNG', 'ES', 'EDG', 'LGD', 'IG', 'BLG', 'TES', 'SN', 'WE',
             'OMG', 'OMD', 'LNG', 'JDG', 'FPX', 'RW', 'VG', 'V5']

matchdetail_urlpre = 'https://www.shangniu.cn/live/lol/'
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
# print(startTime, lastTime)

# 拼接本周的赛程url
url_matchlist = 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime, lastTime)
# 一周的时间戳差值为604800000
startTime_l = startTime - 604800000
lastTime_l = lastTime - 604800000
# 上周的赛程url
url_matchlist_l= 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime_l, lastTime_l)


def parse(url, headers):
    now_1 = time.time()
    response_match = get_response(url, headers)
    response_match = response_match['body']
    # print('赛程个数和结果：', len(response_match), response_match)
    for response_each in response_match:
          team_a_name = response_each['teamAShortName']
          team_b_name = response_each['teamBShortName']
          status = response_each['status']
          # 过滤掉未进行的比赛
          if status != 0 and team_a_name in LPL_list and team_b_name in LPL_list:
                # 过滤只拿LPL的赛程,且比赛为已完成或者进行中的数据
                # 暂时不确定进行中的数据是否和已完成一样，要等下午对局开始在确定
                if team_a_name in LPL_list and team_b_name in LPL_list:
                      bo = response_each['bo']
                      # print('过滤留下来的赛程队伍：', team_a_name, team_b_name, bo, type(bo))
                      matchId = response_each['matchId']
                      # 拼接对局详情url
                      matchdetail_url = matchdetail_urlpre + matchId
                      # print('对局详情url：', matchdetail_url)
                      # 请求对局详情url
                      requests.packages.urllib3.disable_warnings()
                      response_detail = requests.get(matchdetail_url, headers, verify=False)
                      response_detail = response_detail.text
                      html = etree.HTML(response_detail)

                      # 用xpath拿到对局详情页的battle_id,拼接对局详情数据的url,以及场次数
                      battle_id = str(html.xpath('/html/body/script[1]/text()'))
                      # print('html源数据：', battle_id)
                      battle_id_str = battle_id.split('battle_id:')[1]
                      battle_id = int(battle_id_str.split(',')[0])
                      # print('xpath拿到的battle_id：', battle_id)
                      # 根据bo场次和battle_id拼接小场的详情数据url（先拼接url,没打满的会过滤掉）
                      bo_count = bo
                      battle_urls = []
                      while bo_count > 0:
                            battledetail_url = 'https://www.shangniu.cn/api/battle/lol/match/liveBattle?' \
                                               'battleId={}'.format(battle_id)
                            battle_urls.append(battledetail_url)
                            battle_id -= 1
                            bo_count -= 1
                      print(battle_urls)
    now_2 = time.time()
    print(now_2 - now_1)

# def parse_detail():








parse(url_matchlist, headers_yxlmgw)







