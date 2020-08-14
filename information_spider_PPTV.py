# -*-coding:utf-8-*-
from import_data_to_mysql import con_db
from setting import db_sport_setting
from common_tool import request_xpath, redis_check
from datetime import datetime
import requests

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

start_url_O = {
    Spain_url:'西甲联赛', German_url:'德甲联赛', Italy_url:'意甲联赛', France_url:'法甲联赛'
}

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/84.0.4147.125 Safari/537.36'
}
article_url_pre = 'http://www.ppsport.com'

# 英超资讯只抓两部分
def parse_E(url, league_name):
    types = 1
    source_from = 'PP体育足球资讯'

    html = request_xpath(url, headers)
    # 拿到文章id用于拼接文章详情的url(第一部分)
    article_ids = html.xpath('/html/body/div[1]/div[4]/div[2]/div[3]/dl[1]/dd/a/@href')
    # print(len(article_ids), article_ids)
    for article_id_url in article_ids:
        # 提取article_id
        article_id = article_id_url.split('/')[-1]
        article_id = article_id.split('.')[0]
        article_url = article_url_pre + article_id_url
        print('第一部分文章id和详情url:', article_id, article_url)

        # 拿到字段信息
        html_artile = request_xpath(article_url, headers)
        article_title = html_artile.xpath('/html/body/div[1]/div[3]/div[2]/div/div[1]/h1/text()')[0]
        article_date_author = html_artile.xpath('/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/text()')[0]
        # 咨询时间和资讯作者连在一起
        article_date_author = article_date_author.split('PP体育 |')
        article_date = article_date_author[0]
        article_date = article_date.replace('年', '-')
        article_date = article_date.replace('月', '-')
        article_date = article_date.replace('日', '')
        article_date = article_date.strip()
        print(article_date)
        article_date = datetime.strptime(article_date, '%Y-%m-%d %H:%M:%S')
        article_author = article_date_author[1]
        article_author = article_author.strip()
        contents = html_artile.xpath('//*[@id="articleContent"]/p/text()')
        article_content = ''
        for content in contents:
            article_content += content
        article_img = html_artile.xpath('//*[@id="articleContent"]/div[1]/img/@src')
        article_img = str(article_img)
        article_img = article_img.replace('\'', '\"')
        print('资讯信息:',article_content)

        sql_insert = "INSERT INTO `information_football`(type, league_name, source_from, article_id, article_title, " \
        "article_date, article_author, article_img, article_content) VALUES({0}, '{1}', '{2}', {3}, '{4}', '{5}', " \
        "'{6}', '{7}', '{8}')" \
                     "ON DUPLICATE KEY UPDATE " \
        "type={0}, league_name='{1}', source_from='{2}', article_id={3}, article_title='{4}', article_date='{5}', " \
        "article_author='{6}', article_img='{7}', article_content='{8}'".format(types, league_name, source_from, article_id,
        article_title, article_date, article_author, article_img, article_content)
        print('开始写入的sql:', sql_insert)
        db.update_insert(sql_insert)
        print('更新或插入完成')



parse_E(England_url, '英超联赛')





