# '''
# 使用单例模式创建redis 链接池
# '''
# from redis import ConnectionPool
# import threading
# import time
# class redis_pool(object):
#     _instance_lock = threading.Lock()
#     pool = ConnectionPool(host='localhost', port=6379, db=0)
#     def __init__(self):
#         time.sleep(1)
#
#     @classmethod
#     def instance(cls, *args, **kwargs):
#         if not hasattr(redis_pool, "_instance"):
#             with redis_pool._instance_lock:
#                 if not hasattr(redis_pool, "_instance"):
#                     redis_pool._instance = redis_pool(*args, **kwargs)
#         return redis_pool._instance
#
# if __name__ == "__main__":
#     def task(arg):
#         obj = redis_pool.instance()
#         print(obj)
#         print(obj.pool)
#     for i in range(10):
#         t = threading.Thread(target=task,args=[i,])
#         t.start()
#         time.sleep(2)
#     print('end')
#     obj = redis_pool.instance()
#     print(obj)
#     print(obj.pool)

import test
