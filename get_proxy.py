# -*-coding:utf-8-*-
'''
生成代理
'''
import requests
import time
import json


try:
    get_proxies_urls = "http://d.jghttp.golangapi.com/getip?num=5&type=2&pro=&city=0&yys=0&port=1&pack=21866&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=3&regions="
    resp = requests.get(get_proxies_urls, timeout=5)
    text = resp.text
    list = json.loads(text)
    print(list)
    if list['code'] == 0:
        # 极光代理会返回5个代理ip,每天发放1000个代理
        # 每个代理ip时效5-25分钟
        # 在定时任务中定时7分钟执行
        # print(list)
        file2 = open('proxies.txt', 'w')
        try:
            for ips in list['data']:
                pro_text = ips['ip'] + ':' + str(ips['port'])
                file2.write(pro_text + '\n')
                # print(pro_text)
        finally:
            file2.close()

except requests.exceptions.RequestException as e:
    print(e)