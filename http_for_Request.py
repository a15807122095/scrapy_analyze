# -*-coding:utf-8-*-
from flask import Flask,render_template,request
from import_data_to_mysql import con_db
from game_match_spider_wanplus import start_url_wanplus, headers_wanplus, parse_wanplus, monday_stamp, next_weekstamp

# 创建mysql对象
db = con_db()

app = Flask(__name__)

# 后端通过调用接口来启动爬虫脚本
"""
wanplus -- 英雄联盟lpl之外的赛程
"""
@app.route('/wanplus')
def match_list_wanplus():
    # 本周的赛程
    # print('开始抓本周赛程')
    form_data = {
        '_gtk': 806653903,
        'game': 2,
        'time': monday_stamp,
        'eids': ''
    }
    parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
    # print('本周赛程已抓取')
    # # 下周的赛程
    # print('开始抓下周赛程')
    form_data = {
        '_gtk': 806653903,
        'game': 2,
        'time': next_weekstamp,
        'eids': ''
    }
    parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
    # print('下周赛程已抓取')
    return 'wanplus已抓取完成'

# """
# wanplus -- 王者荣耀赛程
# """
# @app.route('/wzry')
# def match_list_wanplus():
#     for url in url_groups_wzry:
#         propertys = '小组赛'
#         parse_wzry(url, header_wzry, propertys, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8500)

