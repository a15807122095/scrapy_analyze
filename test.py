'''
使用单例模式创建redis 链接池
'''

from datetime import datetime

stamp1 = 1592736925
stamp2 = 1592478000

stamp_now1 = datetime.fromtimestamp(stamp1)
print(stamp_now1)
stamp_now2 = datetime.fromtimestamp(stamp2)
print(stamp_now2)