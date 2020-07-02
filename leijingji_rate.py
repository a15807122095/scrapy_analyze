# -*-coding:utf-8-*-
import time
import requests
from datetime import datetime, timedelta
from common_tool import get_response
from lxml import etree
from common_tool import api_check
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_checkAPI

"""
雷竞技网英雄联盟赔率爬虫
"""
# 爬虫流程：
# 开始加载两页赛程的url：start_url， second_url
# start_url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'，
# second_url ='https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=2'
# 从start_url和second_url中拿到id，拼凑得到详情url
# 详情url中拿到对应赔率url：https://incpgameinfo.esportsworldlink.com/v2/odds?match_id=37219633

start_url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'
second_url ='https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=2'

match_url_start = 'https://incpgameinfo.esportsworldlink.com/v2/odds?match_id='

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

def parse(url, headers):
    responses = get_response(url, headers)
    responses = responses['result']
    print('源数据：', len(responses))
    types = 1
    source = '雷竞技'
    for response in responses:
        game_name = response['game_name']
        # 过滤只拿到英雄联盟的赔率
        if game_name == '英雄联盟':
            id = response['id']
            # print('网站的赛事id：',id)
            match_url = match_url_start + str(id)
            # print('详情赔率url:', match_url)
            responses_detail = get_response(match_url, headers)
            responses_detail = responses_detail['result']
            print('详情数据：', responses_detail)
            bo = responses_detail['round'][-1:]
            board_num = int(bo)
            # 0-139条赔率数据，每两组构成一条数据库中的数据
            for rate_message in responses_detail['odds']:
                title = rate_message['']


parse(start_url, headers)
parse(second_url, headers)

