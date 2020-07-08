# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from lxml import etree
from import_data_to_mysql import con_db

"""
竞彩网赔率爬虫
"""

db = con_db()


bet_list = {
    'u-cir':2, 'u-dan':1, 'u-kong':0
}

headers_bet = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

start_url = 'https://info.sporttery.cn/football/match_list.php'

match_betdetail = 'https://www.lottery.gov.cn/football/match_hhad.jspx?mid='

response = requests.get(url=start_url, headers=headers_bet)
response = response.content.decode('gb2312')
html = etree.HTML(response)

messages = html.xpath("//div[@class='match_list']/table//tr")
for message in messages:
    s_id = message.xpath('td[3]/a/@href')
    # 如果赛程id不为空才继续抓取其余信息
    if s_id:
        s_id = s_id[0]
        s_id = s_id.split('m=')[1]
        match_beturl = match_betdetail + s_id
        # print(match_beturl)

url = 'https://www.lottery.gov.cn/football/match_hhad.jspx?mid=125342'
response_bet = requests.get(url=url, headers=headers_bet)
response_bet = response_bet.text
html_1 = etree.HTML(response_bet)
bet = html_1.xpath('//table[@class="table2 yylMt20"]//td[3]')
print(bet)




