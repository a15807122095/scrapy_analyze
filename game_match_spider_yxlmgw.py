# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from common_tool import api_check
from import_data_to_mysql import con_db
from setting import url_finish, url_matching, url_unfinish, headers_yxlmgw

"""
英雄联盟官网爬虫
"""

def parse(url, match_status):
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url=url, headers=headers_yxlmgw, verify = False)
    sources = response.text
    sources = json.loads(sources)

    # 没有进行的比赛不解析 （没有进行比赛status为'-1'）
    if sources['status'] != '-1':
        sources = sources['msg']['result']
        print('爬取的源数据：',len(sources), sources)
        game_name = '英雄联盟'
        type = 1
        status = match_status
        for each_source in sources:
            bo = each_source['GameMode']
            team_a_score = each_source['ScoreA']
            team_b_score = each_source['ScoreB']
            if each_source['MatchWin'] == '1':
                win_team = 'A'
            elif each_source['MatchWin'] == '2':
                win_team = 'B'
            else:
                win_team = None
            print('比分数据：',type, status, bo, team_a_score, team_b_score, win_team)
            league_sourcename = each_source['GameName'] + each_source['GameTypeName']
            # 匹配A，B的名字
            bMatchName = each_source['bMatchName']
            bMatchName = bMatchName.split('vs')
            team_a_sourcename = bMatchName[0].strip()
            team_b_sourcename = bMatchName[1].strip()
            start_time = each_source['MatchDate']
            # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
            check_match= league_sourcename + team_a_sourcename + team_b_sourcename + start_time
            sql_check = 'select id from game_python_match where check_match = "{}"'.format(check_match)
            print('访问接口前的sql：', sql_check)
            status_check = db.select_id(sql_check)
            print('访问接口前的拼接字符串和匹配到的主键：', status_check, check_match)
            if status_check == None:
                # 请求检测接口
                result = api_check(game_name, league_sourcename, team_a_sourcename, team_b_sourcename)
                print('检测接口返回：',result)
                # 检测为600, result['result']包含6个字段：
                # league_id, team_a_id, team_b_id,
                # league_name, team_a_name, team_b_name
                if result['code'] == 600:
                    result_insert = result['result']
                    league_id = result_insert['league_id']
                    team_a_id = result_insert['team_a_id']
                    team_b_id = result_insert['team_b_id']
                    league_name = result_insert['league_name']
                    team_a_name = result_insert['team_a_name']
                    team_b_name = result_insert['team_b_name']
                    # 将爬取的字符串时间转化为datetime类型
                    date = datetime.strptime(each_source['MatchDate'], '%Y-%m-%d %H:%M:%S')
                    # 转化为时间戳
                    date_timestamp = int(time.mktime(date.timetuple()))
                    # 将result_insert和date_timestamp与game_python_match进行对比确定是否有这场赛事
                    sql_check = 'select id from game_python_match where league_id = {0} and team_a_id = {1} ' \
                                'and team_b_id = {2} and start_time = {3}'.format(league_id, team_a_id, team_b_id,
                                                                                  date_timestamp)
                    print('600的查询主键sql：', sql_check)
                    status_update_or_insert = db.select_id(sql_check)
                    print('600的查询主键：', status_update_or_insert)
                    if status_update_or_insert == None:
                        # 确定没有这场赛事就执行插入数据
                        # 拿到其余需要更新的字段
                        sql_insert = "INSERT INTO `game_python_match` (type, league_id, status, start_time, bo," \
                                     " team_a_id, team_a_name, team_a_score, team_b_id, team_b_name, team_b_score, " \
                                     "league_name, check_match, win_team) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, '{6}', " \
                                     "{7}, {8}, '{9}', {10}, '{11}', '{12}', '{13}');".format(type, league_id, status,
                                     date_timestamp, bo, team_a_id, team_a_name, team_a_score, team_b_id, team_b_name,
                                     team_b_score, league_name, check_match, win_team)
                        print('600的未有记录执行插入：', sql_insert)
                        db.update_insert(sql_insert)
                        print('600的未有记录执行插入完成')
                    else:
                        print('600的有记录执行修改', type, status, bo, team_a_score, team_b_score, win_team, check_match,
                              status_update_or_insert)
                        db.update_by_id(type, status, bo, team_a_score, team_b_score, win_team, check_match,
                                        status_update_or_insert)
                        print('600的有记录执行修改完成')

                elif result['code'] == 200:
                    # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                    insert_blacklist = result['result']
                    league_name = insert_blacklist['league_name'] if insert_blacklist['league_id'] == '0' else None
                    team_a_name = insert_blacklist['team_a_name'] if insert_blacklist['team_a_id'] == '0' else None
                    team_b_name = insert_blacklist['team_b_name'] if insert_blacklist['team_b_id'] == '0' else None
                    sql_blacklist = "INSERT INTO `game_python_match` (team_a_name, team_b_name, league_name) VALUES" \
                          " ({0}, {1}, {2});".format(team_a_name, team_b_name, league_name)
                    print('200的添加到api_check_200表中sql：', sql_blacklist)
                    db.update_insert(sql_blacklist)
                    print('200的添加到api_check_200表中sql完成')
            # 本地已有数据就直接更新
            else:
                print('本地已有数据就直接更新 ')
                # 这里把check_match拿进去再更新一次没关系
                db.update_by_id(type, status, bo, team_a_score, team_b_score, win_team, check_match, status_check)
                print('本地已有数据就直接更新完成')










if __name__ == '__main__':
    # 创建mysql连接对象
    db = con_db()
    # 拿到时间戳
    now_time = time.time()
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
# url_11 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&p10=&p6=2&p11=&p12=&page=1&pagesize=2&r1=retObj&_=1591751448292'


# # 进行中
# url_2 =  'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=9999&r1=retObj&_=1591712995985'

#{"status":"-1","msg":"\u672a\u67e5\u8be2\u5230\u76f8\u5173\u6570\u636e\u3002"}

# # 未完成
# url_3  = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&p10=&p6=3&p11=&p12=&page=1&pagesize=10&r1=retObj&_=1591712996084'



