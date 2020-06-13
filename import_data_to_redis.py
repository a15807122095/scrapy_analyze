# -*-coding:utf-8-*-

# 先将爬取的源数据去重存入mongo中，然后让mysql进行读写操作
# 导入redis模块
import redis

class con_redis():

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

