import requests
import pymysql
import time
from datetime import datetime
from common_tool import api_check
string = '2020-06-11 19:00:00'
string = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

# 2020职业联赛夏季赛常规赛ESFPX2020-06-27 19:00:00
league_name =  '2020职业联赛夏季赛常规赛'
str = league_name[-3:]
print(str)
