# '''
# 使用单例模式创建redis 链接池
# '''
import requests
import json
url_wzrygw = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage1.json'
headers_wzrygw = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}



requests.packages.urllib3.disable_warnings()
response = requests.get(url=url_wzrygw, headers=headers_wzrygw, verify = False)
response = response.text
response = json.loads(response)
sources = response['matchList']
print('抓取到的源数据：',len(sources), sources)