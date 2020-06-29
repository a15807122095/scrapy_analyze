# -*-coding:utf-8-*-
import json
import requests
from common_tool import get_response, api_check, check_local, API_return_600, API_return_200
from lxml import etree
from datetime import datetime
from setting import headers_wzrygw


"""
王者荣耀官网爬虫
"""

url = 'https://pvp.qq.com/match/kcc.shtml'

response = requests.get(url=url, headers=headers_wzrygw)
response = response.text
html = etree.HTML(response)

result = html.xpath('/html/body/div[1]/div/div[4]/div[4]/div[2]/div/div/div[3]/div/div/div[2]/div[1]/div[2]')
print(result)