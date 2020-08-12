# -*-coding:utf-8-*-

from flask import Flask, request
import json
from game_match_spider_yxlmgw import run_game_match_spider_yxlmgw
from game_match_spider_wanplus import run_game_match_spider_wanplus


app = Flask(__name__)

"""
此脚本用于将爬虫脚本以HTTP请求方式调用
"""

# 英雄联盟LPL赛程爬虫
@app.route("/game_match_spider_yxlmgw", methods=["GET"])
def match_yxlmgw():
    try:
        run_game_match_spider_yxlmgw()
        return_dict = {'code': '200', 'result': '英雄联盟LPL赛程爬虫已完成'}
    except Exception as e:
        return_dict = {'code': '500', 'result': '英雄联盟LPL赛程爬虫抓取失败...'}
    return json.dumps(return_dict, ensure_ascii=False)

# 英雄联盟其他赛区赛程爬虫
@app.route("/game_match_spider_wanplus", methods=["GET"])
def match_wanplus():
    try:
        run_game_match_spider_wanplus()
        return_dict = {'code': '200', 'result': '英雄联盟其他赛区赛程爬虫已完成'}
    except Exception as e:
        return_dict = {'code': '500', 'result': '英雄联盟其他赛区赛程爬虫抓取失败...'}
    return json.dumps(return_dict, ensure_ascii=False)

# 英雄联盟LPL赛程爬虫
@app.route("/game_match_spider_wanplus", methods=["GET"])
def match_wanplus():
    try:
        run_game_match_spider_wanplus()
        return_dict = {'code': '200', 'result': '英雄联盟其他赛区赛程爬虫已完成'}
    except Exception as e:
        return_dict = {'code': '500', 'result': '英雄联盟其他赛区赛程爬虫抓取失败...'}
    return json.dumps(return_dict, ensure_ascii=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)