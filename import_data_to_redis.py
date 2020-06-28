# -*-coding:utf-8-*-


# 导入redis模块

'''
使用单例模式创建redis 链接池
'''
from redis import ConnectionPool

import redis

# 检测后端API之前现在redis中查询是否有记录/尚牛网存储本周和上周的url以及
# 查询赛事id时要先访问后端接口返回规范的队伍名,保存到redis,然后再找到赛事的id
# 下次再找赛事id先访问redis，有记录直接拿到主键
# redis中存储的格式：str（ 源网站 + 源数据联赛名 + 源数据A队名 + 源数据B队名 + 比赛时间 ) : str（源网站+主键）
# 尚牛url：week1/url_matchlist, week2/url_matchlist_l
class RedisDBConfig_checkAPI:
    HOST = '127.0.0.1'
    PORT = 6379
    DBID = 0

class RedisCache_checkAPI(object):
    def __init__(self):
        if not hasattr(RedisCache_checkAPI, 'pool'):
            RedisCache_checkAPI.create_pool()
        self._connection = redis.Redis(connection_pool=RedisCache_checkAPI.pool)

    @staticmethod
    def create_pool():
        RedisCache_checkAPI.pool = redis.ConnectionPool(
            host=RedisDBConfig_checkAPI.HOST,
            port=RedisDBConfig_checkAPI.PORT,
            db=RedisDBConfig_checkAPI.DBID)

    # @operator_status
    def set_data(self, key, time, value):
        '''set data with (key, value)
        '''
        return self._connection.setex(key, time, value)

    # @operator_status
    def get_data(self, key):
        '''get data by key
        '''
        if self._connection.get(key):
            return self._connection.get(key).decode('utf-8')
        else:
            return None

    # @operator_status
    def del_data(self, key):
        '''delete cache by key
        '''
        return self._connection.delete(key)



# 为了减少数据库读写太频繁，已完成和未进行的因为基本一天之内没变化，赛程录入到redis，
# 后续从redis检查到记录就过滤掉，因为进行中的比赛变化比较频繁，不考虑redis缓存
class RedisDBConfig_urldistict:
    HOST = '127.0.0.1'
    PORT = 6379
    DBID = 1


class RedisCache_urldistict(object):
    def __init__(self):
        if not hasattr(RedisCache_urldistict, 'pool'):
            RedisCache_urldistict.create_pool()
        self._connection = redis.Redis(connection_pool=RedisCache_urldistict.pool)

    @staticmethod
    def create_pool():
        RedisCache_urldistict.pool = redis.ConnectionPool(
            host=RedisDBConfig_urldistict.HOST,
            port=RedisDBConfig_urldistict.PORT,
            db=RedisDBConfig_urldistict.DBID)

    def set_data(self, key, time, value):
        '''设
        '''
        return self._connection.setex(key, time, value)

    def get_data(self, key):
        '''查
        '''
        if self._connection.get(key):
            return self._connection.get(key).decode('utf-8')
        else:
            return None

    def del_data(self, key):
        '''删
        '''
        return self._connection.delete(key)







