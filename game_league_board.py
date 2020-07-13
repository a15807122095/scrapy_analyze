# -*-coding:utf-8-*-

import requests
import json
from common_tool import get_response

"""
联赛积分榜
（英雄联盟，王者荣耀在一张表）
"""

start_url = 'https://info.sporttery.cn/football/match_list.php'

header = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

