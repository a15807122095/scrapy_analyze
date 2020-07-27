# '''
# 使用单例模式创建redis 链接池
# '''
import json
from lxml import etree
from common_tool import player_check, team_check, api_check, league_check, hero_check
from datetime import datetime
from import_data_to_mysql import con_db
from setting import db_setting
import requests
from lxml import etree

#
# time1 = 1593446400
# str = datetime.fromtimestamp(time1)
# print(str)

# #查询2020-06-30当日的数据
# str1 = '2020-07-23 00:00:00'
# str2 = '2020-07-25 00:00:00'
# #
# date1 = datetime.strptime(str1, '%Y-%m-%d %H:%M:%S')
# date2 = datetime.strptime(str2, '%Y-%m-%d %H:%M:%S')
# print(date1, date2)
#
# stamp1 = int(date1.timestamp())
# stamp2 = int(date2.timestamp())
# print(stamp1, stamp2)
#
# sql = 'select * from game_python_match where start_time between {0} and {1};'.format(stamp1, stamp2)
# print(sql)


# result = api_check('王者荣耀', '2020世界冠军杯', 'ROX Phoenix', '成都AG超玩会')
# print(result)
#
result = league_check('2017 KPL秋季赛', 2)
print(result)
#
# result = team_check('王者荣耀', '2020世界冠军杯')
# print(result)
#
# result = player_check('王者荣耀', '2020世界冠军杯')
# print(result)
#
# result = hero_check('王者荣耀', '2020世界冠军杯')
# print(result)


