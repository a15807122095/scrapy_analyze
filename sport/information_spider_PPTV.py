# -*-coding:utf-8-*-
from import_data_to_mysql import con_db
from setting import db_sport_setting

"""
五大联赛资讯爬虫
抓取规则:五大联赛对应的start_url
用xpath提取

"""

db = con_db(db_sport_setting['host'], db_sport_setting['user'], db_sport_setting['password'], db_sport_setting['db'])

England_url = 'http://www.ppsport.com/premierleague'
Spain_url = 'http://www.ppsport.com/laliga'
German_url = 'http://www.ppsport.com/bundesliga'
Italy_url = 'http://www.ppsport.com/seriea'
France_url = 'http://www.ppsport.com/ligue1'

start_url_ = [England_url, Spain_url, German_url, Italy_url, France_url]



def parse():
