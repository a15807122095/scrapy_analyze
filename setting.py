

"""
游戏dev配置
"""
db_setting = {
    'host': '127.0.0.1',
    'user': 'root',
    'password' : '0000',
    'db' : 'Game'
}

"""
体育dev配置
"""
db_sport_setting = {
    'host': '127.0.0.1',
    'user': 'root',
    'password' : '0000',
    'db' : 'Sport'
}



Redis_checkAPI = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}
Redis_urldistict = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 1
}


## product
# db_setting = {
#     'host': '116.62.47.187',
#     'user': 'ele_python',
#     'password' : 'ele_python',
#     'db' : 'ele_python'
# }

# """
# 生产环境查询联赛id和战队id
# """
# db_product_setting = {
#     'host': '121.40.95.117',
#     'user': 'ele_sports',
#     'password' : 'ele_sports',
#     'db' : 'ele_sports'
# }

# product
# db_sport_setting = {
#     'host': '116.62.47.187',
#     'user': 'nami_sports',
#     'password' : 'nami_sports',
#     'db' : 'nami_sports'
# }

# """
# 体育product配置
# """
# db_sport_setting = {
#     'host': '127.0.0.1',
#     'user': 'root',
#     'password' : '0000',
#     'db' : 'Sport'
# }

# Redis_checkAPI = {
#     'host': '127.0.0.1',
#     'port': 6379,
#     'db': 0
# }
#
# Redis_urldistict = {
#     'host': '127.0.0.1',
#     'port': 6379,
#     'db': 1
# }




# 王者荣耀官网的url  headers   # 已废弃
# 官网默认加载2页
url_wzrygw_1 = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage1.json'
url_wzrygw_2 = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage2.json'
url_wzrygw = [url_wzrygw_1, url_wzrygw_2]
headers_wzrygw = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

proxy_pool = {
    "http": "180.127.81.154:4534"
}

