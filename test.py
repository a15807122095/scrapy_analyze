'''
使用单例模式创建redis 链接池
'''
import requests
from setting import proxy_pool
headers_yxlmgw = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    }

url1 = 'https://www.shangniu.cn/live/lol/'
url2 = 'http://icanhazip.com'
response = requests.get(url2, headers_yxlmgw, proxies=proxy_pool)
print(response.text)
print(response)
response1 = requests.get(url1, headers_yxlmgw, proxies=proxy_pool)
print(response1)
