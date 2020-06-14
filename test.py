import requests
import pymysql
import time
from datetime import datetime
from setting import db_setting
string = '2020-06-11 19:00:00'
string = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

result = {
    'a': '0',
    'a1':'a1的名字',
    'b': '321',
    'b1':'b1的名字',
}

result_a = result['a1'] if result['a'] == '0' else None
result_b = result['b1'] if result['b'] == '0' else None

print(result_a, result_b)