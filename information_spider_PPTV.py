# -*-coding:utf-8-*-
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_urldistict
from setting import db_sport_setting
from common_tool import request_xpath, redis_check_article, get_log
from datetime import datetime
import json

"""
五大联赛资讯爬虫
抓取规则:五大联赛对应的start_url找到article_id,拼接成咨询详情页的url
用xpath提取
"""

redis = RedisCache_urldistict()
db = con_db(db_sport_setting['host'], db_sport_setting['user'], db_sport_setting['password'], db_sport_setting['db'])

England_url = 'http://www.ppsport.com/premierleague'
Spain_url = 'http://www.ppsport.com/laliga'
German_url = 'http://www.ppsport.com/bundesliga'
Italy_url = 'http://www.ppsport.com/seriea'
France_url = 'http://www.ppsport.com/ligue1'

information_pptv_log = get_log('information_pptv')

# 五大联赛对应联赛归属
start_url_O = {
    England_url:'英超联赛', Spain_url:'西甲联赛', German_url:'德甲联赛', Italy_url:'意甲联赛', France_url:'法甲联赛'
}

# 五大联赛的网页对应的提取资讯id的xpath规则:
# 英超是两个板块,其他联赛是三个板块(三个板块xpath规则目前看起来是一样)
# 提取的资讯id格式为('/article/news/1042662.html'),直接凭借成咨询详情页
league_xpath_rule = {
    England_url: {
        '/html/body/div[1]/div[4]/div[2]/div[3]/dl[1]/dd/a/@href',
        '/html/body/div[1]/div[4]/div[6]/div[2]/div/div/div/div/a/@href'
    },
    Spain_url:{
        '/html/body/div[1]/div[4]/div[3]/div[3]/div[1]/div/dl/dd/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[2]/div/div/div/div/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[1]/div[1]/div/dl/dd/a/@href'
    },
    German_url:{
        '/html/body/div[1]/div[4]/div[3]/div[3]/div[1]/div/dl/dd/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[2]/div/div/div/div/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[1]/div[1]/div/dl/dd/a/@href'
    },
    Italy_url:{
        '/html/body/div[1]/div[4]/div[3]/div[3]/div[1]/div/dl/dd/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[2]/div/div/div/div/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[1]/div[1]/div/dl/dd/a/@href'
    },
    France_url:{
        '/html/body/div[1]/div[4]/div[3]/div[3]/div[1]/div/dl/dd/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[2]/div/div/div/div/a/@href',
        '/html/body/div[1]/div[4]/div[3]/div[1]/div[1]/div/dl/dd/a/@href'
    }
}


headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/84.0.4147.125 Safari/537.36'
}
article_url_pre = 'http://www.ppsport.com'

# 英超资讯只抓两部分
def parse(url, league_name, xpath_url):
    types = 1
    source_from = 'PP体育足球资讯'

    html = request_xpath(url, headers)
    # 拿到文章id用于拼接文章详情的url(第一部分)
    article_ids = html.xpath(xpath_url)
    # print(len(article_ids), article_ids)
    for article_id_url in article_ids:
        try:
            # 提取article_id
            article_id = article_id_url.split('/')[-1]
            article_id = article_id.split('.')[0]

            article_url = article_url_pre + article_id_url
            print('文章id和详情url:', article_id, article_url)

            article_id_judge = article_id.isdigit()
            print(article_id_judge)
            # article_id必须为数字
            if article_id_judge:
                parse_detail(article_url, headers, types, league_name, source_from, article_id)
        except Exception as e:
            information_pptv_log.error(e)


# 详情页解析
def parse_detail(article_url, headers, types, league_name, source_from, article_id):
    # 校验redis中是否有数据
    redis_key = 'PP体育足球资讯'
    judge_sql = "select id from information_football where source_from='{0}' and article_id={1};". \
        format(source_from, article_id)
    judge_arg = redis_check_article(redis_key, article_id, judge_sql, redis, db)
    print('sql检测:', judge_arg, judge_sql)

    # redis和表中都没有article_id的记录,开始录入到表中
    if judge_arg:

        # 拿到字段信息
        html_artile = request_xpath(article_url, headers)
        print('详情的xpath解析:', html_artile)
        article_title = html_artile.xpath('/html/body/div[1]/div[3]/div[2]/div/div[1]/h1/text()')
        article_title = article_title if article_title else None
        # 有的资讯id拼接的详情页不是新闻,通过标题的有无过滤掉
        if article_title:
            article_date_author = html_artile.xpath('/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/text()')[0]

            contents = html_artile.xpath('//*[@id="articleContent"]/p/text()')
            article_content = ''
            for content in contents:
                article_content += content
            article_img = html_artile.xpath('//*[@id="articleContent"]/div[1]/img/@src')
            article_img = str(article_img)
            article_img = article_img.replace('\'', '\"')
            print('资讯信息:', type(article_img), article_content)

            # 判断是否为纯video的资讯(资讯图片和资讯内容为空)
            if article_img != '[]' and article_content:

                # 咨询时间和资讯作者连在一起(也有无作者的情况,要判断)
                if 'PP体育 |' in article_date_author:
                    article_date_author = article_date_author.split('PP体育 |')
                    article_date = article_date_author[0]
                    article_author = article_date_author[1]
                    article_author = article_author.strip()
                else:
                    # 作者没有的话用'佚名'代替
                    article_date = article_date_author
                    article_author = '佚名'
                article_date = article_date.replace('年', '-')
                article_date = article_date.replace('月', '-')
                article_date = article_date.replace('日', '')
                article_date = article_date.strip()
                article_date = datetime.strptime(article_date, '%Y-%m-%d %H:%M:%S')
                # print(article_date)

                sql_insert = "INSERT INTO `information_football`(type, league_name, source_from, article_id, article_title, " \
                "article_date, article_author, article_img, article_content) VALUES({0}, '{1}', '{2}', {3}, \"{4}\", '{5}', " \
                "'{6}', '{7}', \"{8}\")" \
                             "ON DUPLICATE KEY UPDATE " \
                "type={0}, league_name='{1}', source_from='{2}', article_id={3}, article_title=\"{4}\", article_date='{5}', " \
                "article_author='{6}', article_img='{7}', article_content=\"{8}\";".format(types, league_name, source_from,
                article_id, article_title, article_date, article_author, article_img, article_content)
                print('开始写入的sql:', sql_insert)
                db.update_insert(sql_insert)
                print('更新或插入完成')



for url, url_xpaths in league_xpath_rule.items():
    league_name = start_url_O[url]
    print('抓取的联赛归属:', league_name)
    for url_xpath in url_xpaths:
        parse(url, league_name, url_xpath)







