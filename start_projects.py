# -*-coding:utf-8-*-
from import_data_to_mysql import con_db
from game_match_spider_yxlmgw import parse_yxlm
from game_match_spider_wzrygw import parse_wzry
from setting import url_finishs, url_matching, url_unfinishs, headers_yxlmgw
import time

if __name__ == '__main__':

    # 拿到时间戳
    date_time = time.time()
    now_time = str(round(date_time * 1000))
    # 创建mysql连接对象
    db = con_db()
    """
    英雄联盟爬虫抓取
    """
    # 0:未开始 1:进行中 2:已结束
    # print('开始抓取已完成比赛')
    for url_finish in url_finishs:
        url_finish += now_time
        parse_yxlm(url_finish, db, '2', headers_yxlmgw)

    # print('开始抓取未进行比赛')
    for url_unfinish in url_unfinishs:
        url_unfinish += now_time
        parse_yxlm(url_unfinish, db, '0', headers_yxlmgw)

    # print('开始抓取进行中比赛')
    url_matching += now_time
    parse_yxlm(url_matching, db, '1', headers_yxlmgw)

    # """
    # 已废弃
    # 王者荣耀爬虫抓取
    # """
    # for url in url_wzrygw:
    #     print('开始抓取比赛')
    #     parse_wzry(url, db, headers_wzrygw)
    #     print('抓取比赛已完成')

