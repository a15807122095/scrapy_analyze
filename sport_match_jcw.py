# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from lxml import etree
from import_data_to_mysql import con_db
from common_tool import get_response, api_check, check_local, API_return_600, API_return_200

"""
竞彩网赛程爬虫
"""

headers_sport = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

start_url = 'https://info.sporttery.cn/football/match_list.php'

response = requests.get(url=start_url, headers=headers_sport)
response = response.content.decode('gb2312')
html = etree.HTML(response)

messages = html.xpath("//div[@class='match_list']/table//tr")
for message in messages:
    s_name = message.xpath('td[3]/a/@href')
    # 如果赛程id不为空才继续抓取其余信息
    if s_name:
        l_name = message.xpath('td[2]/text()')
        print(s_name, l_name)
        home_team = message.xpath('td[3]/span[1]')
        print(s_name, l_name, home_team)