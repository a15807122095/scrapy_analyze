# -*-coding:utf-8-*-

from setting import Redis_checkAPI, Redis_urldistict
import redis
"""
使用单例模式创建redis 链接池
由于考虑redis可能用法不太一样，定义的时候还是分不同redis库定义
"""
# 检测后端API之前现在redis中查询是否有记录/尚牛网存储本周和上周的url以及
# 查询赛事id时要先访问后端接口返回规范的队伍名,保存到redis,然后再找到赛事的id
# 下次再找赛事id先访问redis，有记录直接拿到主键
# redis中存储的格式：str（ 源网站 + 源网站的赛事id ) : str（源网站+主键）
class RedisCache_checkAPI(object):
    def __init__(self):
        if not hasattr(RedisCache_checkAPI, 'pool'):
            RedisCache_checkAPI.create_pool()
        self._connection = redis.Redis(connection_pool=RedisCache_checkAPI.pool)

    @staticmethod
    def create_pool():
        RedisCache_checkAPI.pool = redis.ConnectionPool(
            host=Redis_checkAPI['host'],
            port=Redis_checkAPI['port'],
            db=Redis_checkAPI['db'],
            password=Redis_checkAPI['password'])

    def set_data(self, key, time, value):
        '''set data with (key, value)
        '''
        return self._connection.setex(key, time, value)

    def get_data(self, key):
        '''get data by key
        '''
        if self._connection.get(key):
            return self._connection.get(key).decode('utf-8')
        else:
            return None

    def del_data(self, key):
        '''delete cache by key
        '''
        return self._connection.delete(key)



# 为了减少数据库读写太频繁,记录选手id（类似于重复查询的redis缓存过滤）
# 后续从redis检查到记录就过滤掉
class RedisCache_urldistict(object):
    def __init__(self):
        if not hasattr(RedisCache_urldistict, 'pool'):
            RedisCache_urldistict.create_pool()
        self._connection = redis.Redis(connection_pool=RedisCache_urldistict.pool)

    @staticmethod
    def create_pool():
        RedisCache_urldistict.pool = redis.ConnectionPool(
            host=Redis_urldistict['host'],
            port=Redis_urldistict['port'],
            db=Redis_urldistict['db'],
            password=Redis_urldistict['password'])

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
