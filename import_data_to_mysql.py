# -*-coding:utf-8-*-
import pymysql
from setting import db_setting

# 现将数据去重存至redis,然后从redis读取再写入mysql

class con_db():
    db = []  # 设置连接池
    __instance = None

    # 判断单例是否存在,不存在就创建否则直接返回
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.db = pymysql.connect(host=db_setting['host'], user=db_setting['user'],
                               password=db_setting['password'], db=db_setting['db'], charset='utf8')
        self.cursor = self.db.cursor()

    # 查询数据库
    def select(self,sql_select):
        self.cursor.execute(sql_select)
        one = self.cursor.fetchall()
        if one != None:
            # 返回查询到的主键
            return one[0]
        else:
            # 未查询到
            return None

    # 更新或插入数据库
    def update_insert(self, sql_modify):
        self.cursor.execute(sql_modify)
        self.cursor.commit()

    def __del__(self):
        # 关闭游标
        self.cursor.close()
        # 关闭数据库
        self.db.close()









class import_mysql():
    def __init__(self, result, import_data):
        conn = pymysql.connect(host=db_setting['host'], user=db_setting['user'],
                               password=db_setting['password'], db=db_setting['db'], charset='utf8')
        self.cursor = conn.cursor()
        # check_data为检测数据， import_data为需要更新添加的数据
        self.result = result
        self.import_data = import_data

    # 拿到联赛名称,队伍A名称, 队伍B名称进行字符串拼接与数据库中进行对比，如果有记录且比赛进行中就直接更新，没记录就请求检测接口
    def check_local_mysql(self,check_string, status):
        sql = 'select id from game_python_match where check_string = "{}";'.format(check_string)
        self.cursor.execute(sql)
        one = self.cursor.fetchone()

        if one != None and status == '1':
            print('这条数据还没请求过检测接口,且是进行中的比赛')
            sql_update = "update game_python_match set team_a_score = {0}, team_b_score = {1} , win_team = '{2}' where id = {3};".format(type, status,
                                                                                        bo, team_a_score, team_b_score,
                                                                                        win_team, one[0])
            print('更新中:', sql_update)
            cursor.execute(sql_update)
            print('已执行更新')
        else:
            print('enter this way 2222')
            sql_insert = "INSERT INTO `game_python_match` (type, league_id, status, start_time, bo, team_a_id, team_a_name," \
                         " team_a_score, team_b_id, team_b_name, team_b_score, league_name, win_team) VALUES ({0}, {1}, {2}, " \
                         "{3}, {4}, {5}, '{6}', {7}, {8}, '{9}', {10}, '{11}', '{12}');".format(type, league_id, status,
                                                                                                start_time,
                                                                                                bo, team_a_id,
                                                                                                team_a_name,
                                                                                                team_a_score, team_b_id,
                                                                                                team_b_name,
                                                                                                team_b_score,
                                                                                                league_name, win_team)
            print('插入中', sql_insert)
            cursor.execute(sql_insert)
            print('已执行插入')
        conn.commit()
        # 关闭游标




    def import_mysql(self):
        # 拿到需要对比的数据:check_data中包含七个字段，但是只需要四个字段与数据库检测匹配：
        # league_id, team_a_id, team_b_id, start_time
        league_id = self.result['league_id']
        team_a_id = self.result['team_a_id']
        team_b_id = self.result['team_b_id']
        start_time = self.result['start_time']

        team_a_name = self.result['team_a_name']
        team_b_name = self.result['team_b_name']
        league_name = self.result['league_name']
        # 更新或插入剩余数据
        type = self.import_data['type']
        status = self.import_data['status']
        bo = self.import_data['bo']
        team_a_score = self.import_data['team_a_score']
        team_b_score = self.import_data['team_b_score']
        win_team = self.import_data['win_team']
        # 查询是否有这条数据并拿到主键
        sql_check = 'select id from game_python_match where league_id = {0} and team_a_id = {1} ' \
                    'and team_b_id = {2} and start_time = {3};'.format(league_id, team_a_id, team_b_id, start_time)
        print(sql_check)
        self.cursor.execute(sql_check)
        one = self.cursor.fetchone()
        print("查询到的记录为：", one)
def import_mysql(self):


    # 查询是否有这条数据并拿到主键
    sql_check = 'select id from game_python_match where league_id = {0} and team_a_id = {1} ' \
                'and team_b_id = {2} and start_time = {3};'.format(league_id,team_a_id,team_b_id,start_time)
    print(sql_check)
    cursor.execute(sql_check)
    one = cursor.fetchone()
    print("查询到的记录为：", one)
    # 执行更新或插入数据库
    if one != None:
        print('enter this way 1111')
        sql_update = "update game_python_match set type = {0}, status = {1}, bo = {2}, team_a_score = {3} ," \
                     "team_b_score = {4} , win_team = '{5}' where id = {6};".format(type, status,
                    bo, team_a_score, team_b_score, win_team, one[0])
        print('更新中:',sql_update)
        cursor.execute(sql_update)
        print('已执行更新')
    else:
        print('enter this way 2222')
        sql_insert = "INSERT INTO `game_python_match` (type, league_id, status, start_time, bo, team_a_id, team_a_name," \
                     " team_a_score, team_b_id, team_b_name, team_b_score, league_name, win_team) VALUES ({0}, {1}, {2}, " \
                    "{3}, {4}, {5}, '{6}', {7}, {8}, '{9}', {10}, '{11}', '{12}');".format(type, league_id, status, start_time,
                    bo, team_a_id, team_a_name, team_a_score, team_b_id, team_b_name, team_b_score, league_name, win_team)
        print('插入中', sql_insert)
        cursor.execute(sql_insert)
        print('已执行插入')
    conn.commit()
    # 关闭游标
    cursor.close()
    # 关闭数据库
    conn.close()
