# -*-coding:utf-8-*-
import pymysql
from setting import db_setting


# 先将数据去重存至redis,然后从redis读取再写入mysql
class con_db():
    db = []
    __instance = None

    # 判断单例是否存在,不存在就创建否则直接返回
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self,host, user, password, db):
        self.db = pymysql.connect(host=host, user=user,
                               password=password, db=db, charset='utf8')
        self.cursor = self.db.cursor()

    # 查询数据库
    def select_message(self, sql_message):
        self.cursor.execute(sql_message)
        message = self.cursor.fetchone()
        return message

    # 查询数据库主键
    def select_id(self,sql_select):
        self.cursor.execute(sql_select)
        one = self.cursor.fetchone()
        # print(one)
        if one != None:
            # 返回查询到的主键
            return one[0]
        else:
            # 未查询到
            return None

    def update_by_id(self, type, status, bo, team_a_score, team_b_score, win_team, check_match,
                     propertys, source_from, source_matchId, start_time, id):
        sql_update =  "update game_python_match set type = {0}, status = {1}, bo = {2}, team_a_score = {3}, " \
                      "team_b_score = {4} , win_team = '{5}', check_match = '{6}', propertys = '{7}', " \
                      "source_from = '{8}', source_matchId = '{9}', start_time={10} where id = {11};".format(type, status,
                       bo, team_a_score, team_b_score, win_team, check_match, propertys, source_from, source_matchId, start_time, id)
        # print('执行修改的sql:', sql_update)
        self.cursor.execute(sql_update)
        self.db.commit()

    # 更新或插入数据库
    def update_insert(self, sql_modify):
        self.cursor.execute(sql_modify)
        self.db.commit()

    def __del__(self):
        # 关闭游标
        self.cursor.close()
        # 关闭数据库
        self.db.close()
