
import json

import requests
import urllib3
import time
from API_check import api_check

# 威客电竞网
url = 'https://ilustre.biz/api/game/reloadpoints/'

headers = {
'Accept': 'application/json, text/plain, */*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9',
'Connection': 'keep-alive',
'Content-Length': '672',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie': '__cdnuid_s=a7eab814f5821129d229b11a80df7a08; __jsluid_s=40c9c5b1efca7c885b7de393e5c2835f; lang=1; css=; PHPSESSID=6l077khiq38sagstr3sqerr6a0',
'Host': 'ilustre.biz',
'Origin': 'https://ilustre.biz',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36X-Requested-With: XMLHttpRequest',
'X-Requested-With': 'XMLHttpRequest'
    }

# Accept: application/json, text/plain, */*
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-CN,zh;q=0.9
# Connection: keep-alive
# Content-Length: 14
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# Cookie: __cdnuid_s=a7eab814f5821129d229b11a80df7a08; __jsluid_s=40c9c5b1efca7c885b7de393e5c2835f; lang=1; css=; PHPSESSID=tdjnl1ageeco50ncev9nuglim0
# Host: ilustre.biz
# Origin: https://ilustre.biz
# Sec-Fetch-Dest: empty
# Sec-Fetch-Mode: cors
# Sec-Fetch-Site: same-origin
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36
# X-Requested-With: XMLHttpRequest

requests.packages.urllib3.disable_warnings()
#
form_data = {
    'point_ids': '1329066',
    'is_liveorfix': '1'
}

response = requests.post(url= url, headers= headers, json=form_data)
response = response.text

print(response)

# picture
url = 'https://static.ilustrepro.com/uploads/20190212/245008e8c79bec28a71e27881a57a7b2.png'

