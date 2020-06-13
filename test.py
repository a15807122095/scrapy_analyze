import requests
import pymysql
import time
from datetime import datetime
from setting import db_setting
string = '2020-06-11 19:00:00'
string = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

import pymysql
class Con_db(object):
    db = []  # 设置连接池
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:#判断单例是否存在,不存在就创建否则直接返回
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.db_host = '127.0.0.1'  #主机地址
        self.db_user = 'root'       #用户名
        self.db_password = '123456' #密码
        self.db_database = 'test'   #要操作的数据库
        self.db = pymysql.connect(host=db_setting['host'], user=db_setting['user'],
                               password=db_setting['password'], db=db_setting['db'], charset='utf8')


class AA(Con_db):
    def __init__(self):
        super().__init__()

    def get_data(self, id):
        sql = 'select team_a_name from game_python_match where id = {};'.format(id)
        con_cursor = self.db.cursor()
        con_cursor.execute(sql)
        data = con_cursor.fetchall()
        print(data)
        print(self.db)
if __name__ == '__main__':
    a1 = AA()
    a1.get_data('23791')
    a2 = AA()
    a1.get_data('23790')

    print(id(a1), id(a2))
