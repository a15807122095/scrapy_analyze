import pymysql
from setting import db_setting

#  check_data为检测数据， import_data为需要更新添加的数据
# def import_mysql(check_data, import_data):
conn = pymysql.connect(host=db_setting['host'], user=db_setting['user'],
                       password=db_setting['password'], db=db_setting['db'], charset='utf8')
cursor = conn.cursor()

# 拿到需要对比的数据:league_id, team_a_id, team_b_id, start_time
# league_id = check_data['league_id']
# team_a_id = check_data['team_a_id']
# team_b_id = check_data['team_b_id']
# start_time = check_data['start_time']
league_id = '268062128'
team_a_id = '183'
team_b_id = '2680672394'
start_time = '1586854800'
type = '2'   # 1
status = '1'  # 2
bo = '5'    # 3
team_a_score = '0'  # 2
team_b_score = '2'   # 0
win_team = 'A'    #A
# 执行数据库对比操作
sql = 'select id from game_python_match where league_id = {0} and team_a_id = {1} ' \
      'and team_b_id = {2} and start_time = {3}'.format(league_id,team_a_id,team_b_id,start_time)
# query = "update 表名 set 字段1 = 值1 where 字段2 = '{}'".format(值2)
sql_2 = "update game_python_match set win_team = '{}' where id = 12109;".format(win_team)
print(sql_2)
cursor.execute(sql_2)
one = cursor.fetchone()
print(one)
conn.commit()
# 关闭游标
cursor.close()
# 关闭数据库
conn.close()