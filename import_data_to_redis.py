# -*-coding:utf-8-*-


# 导入redis模块

'''
使用单例模式创建redis 链接池
'''
from redis import ConnectionPool
from setting import Redis_checkAPI, Redis_urldistict
import redis

# 检测后端API之前现在redis中查询是否有记录/尚牛网存储本周和上周的url以及
# 查询赛事id时要先访问后端接口返回规范的队伍名,保存到redis,然后再找到赛事的id
# 下次再找赛事id先访问redis，有记录直接拿到主键
# redis中存储的格式：str（ 源网站 + 源网站的赛事id ) : str（源网站+主键）
# 尚牛url：week1/url_matchlist, week2/url_matchlist_l
class RedisDBConfig_checkAPI:
    HOST_checkAPI = Redis_checkAPI['host']
    PORT_checkAPI = Redis_checkAPI['port']
    DBID_checkAPI = Redis_checkAPI['db']

class RedisCache_checkAPI(object):
    def __init__(self):
        if not hasattr(RedisCache_checkAPI, 'pool'):
            RedisCache_checkAPI.create_pool()
        self._connection = redis.Redis(connection_pool=RedisCache_checkAPI.pool)

    @staticmethod
    def create_pool():
        RedisCache_checkAPI.pool = redis.ConnectionPool(
            host=RedisDBConfig_checkAPI.HOST_checkAPI,
            port=RedisDBConfig_checkAPI.PORT_checkAPI,
            db=RedisDBConfig_checkAPI.DBID_checkAPI)

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



# 为了减少数据库读写太频繁,记录选手id（类似于重复查询的redis缓存过滤）
# 后续从redis检查到记录就过滤掉
class RedisDBConfig_urldistict:
    HOST_urldistict = Redis_urldistict['host']
    PORT_urldistict = Redis_urldistict['port']
    DBID_urldistict = Redis_urldistict['db']


class RedisCache_urldistict(object):
    def __init__(self):
        if not hasattr(RedisCache_urldistict, 'pool'):
            RedisCache_urldistict.create_pool()
        self._connection = redis.Redis(connection_pool=RedisCache_urldistict.pool)

    @staticmethod
    def create_pool():
        RedisCache_urldistict.pool = redis.ConnectionPool(
            host=RedisDBConfig_urldistict.HOST_urldistict,
            port=RedisDBConfig_urldistict.PORT_urldistict,
            db=RedisDBConfig_urldistict.DBID_urldistict)

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
