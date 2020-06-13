# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from API_check import api_check
from import_data_to_mysql import con_db


# 英雄联盟官网
# 拿到时间戳
now_time = time.time()
headers = {
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

url_finish = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&' \
             'p10=&p6=2&p11=&p12=&page=1&pagesize=2&_='
url_matching = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=9999&_='
url_unfinish = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=10&_='



def parse(url, match_status):
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url=url, headers=headers, verify = False)
    sources = response.text
    sources = json.loads(sources)

    # 没有进行的比赛不解析 （没有进行比赛status为'-1'）
    if sources['status'] != '-1':
        sources = sources['msg']['result']
        print('爬取的源数据：',len(sources), sources)
        game_name = '英雄联盟'
        for each_source in sources:
            league_name = each_source['GameName'] + each_source['GameTypeName']
            # 匹配A，B的名字
            bMatchName = each_source['bMatchName']
            bMatchName = bMatchName.split('vs')
            team_a_name = bMatchName[0].strip()
            team_b_name = bMatchName[1].strip()

            # 请求检测接口
            result = api_check(game_name, league_name, team_a_name, team_b_name)
            print('检测接口返回：',result)
            if result['code'] == 600:
                result_insert = result['result']
                # 将爬取的字符串时间转化为datetime类型
                date = datetime.strptime(each_source['MatchDate'], '%Y-%m-%d %H:%M:%S')
                # 转化为时间戳
                date_timestamp = int(time.mktime(date.timetuple()))
                # 将将时间添加到result中与game_python_match进行对比
                result_insert['start_time'] = date_timestamp
                # 拿到其余需要更新的字段
                import_data = {}
                import_data['type'] = 1
                import_data['status'] = match_status
                import_data['bo'] = each_source['GameMode']
                import_data['team_a_score'] = each_source['ScoreA']
                import_data['team_b_score'] = each_source['ScoreB']
                if each_source['MatchWin'] == '1':
                    import_data['win_team'] = 'A'
                elif each_source['MatchWin'] == '2':
                    import_data['win_team'] = 'B'
                else:
                    import_data['win_team'] = None
                print('更新字段：', import_data)






if __name__ == '__main__':
    # 创建redis连接对象

    # 创建mysql连接对象
    db = con_db()
    url_finish += str(round(now_time * 1000))
    url_matching += str(round(now_time * 1000))
    url_unfinish += str(round(now_time * 1000))
    # 0:未开始 1:进行中 2:已结束
    print('开始抓取已完成比赛')
    parse(url=url_finish, match_status='2')
    print('开始抓取进行中比赛')
    parse(url_matching, match_status='1')
    print('开始抓取未进行比赛')
    parse(url_unfinish, match_status='0')





# # 已完成
# url_1 =  'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=2&r1=retObj&_=1591712542457'
# url_11 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11=&p12=&page=1&pagesize=2&r1=retObj&_=1591751448292'
# url_21 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11=&p12=&page=1&pagesize=2&r1=retObj&_=1591767730245'
# url_31 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11=&p12=&page=1&pagesize=2&r1=retObj&_=1591769388029'
# url_51 =  https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11=&p12=&page=1&pagesize=2&r1=retObj&_=1591856527562
#
# # 进行中
# url_2 =  'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=9999&r1=retObj&_=1591712995985'
# url_22 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=9999&r1=retObj&_=1591751448500'
# url_32 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=9999&r1=retObj&_=1591767730522'
# url_52 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=9999&r1=retObj&_=1591780505084'
#{"status":"-1","msg":"\u672a\u67e5\u8be2\u5230\u76f8\u5173\u6570\u636e\u3002"}

# # 未完成
# url_3  = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=10&r1=retObj&_=1591712996084'
# url_23 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=10&r1=retObj&_=1591751448973'
# url_33 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=10&r1=retObj&_=1591767730647'



