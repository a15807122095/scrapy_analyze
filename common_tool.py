# -*-coding:utf-8-*-
import requests
import json
import time
from datetime import datetime

# # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
def check_local(db, check_match):
        sql_check = 'select id from game_python_match where check_match = "{}"'.format(check_match)
        print('访问接口前的sql：', sql_check)
        status_check = db.select_id(sql_check)
        print('访问接口前的拼接字符串和匹配到的主键：', status_check, check_match)
        return status_check


#  访问后端接口验证是否需要添加记录或是更新记录
# payload = {
#             'game_name': result_game_name,
#             'league_name':result_tournament_name,
#             'team_a_name':result_team_A,
#             'team_b_name':result_team_B,
#            }

def api_check(game_name, league_name, team_a_name, team_b_name):
        payload = {
                'game_name': game_name,
                'league_name': league_name,
                'team_a_name': team_a_name,
                'team_b_name': team_b_name,
        }
        # 请求接口拿到数据
        url_check = 'http://dev.saishikong.com/data/backstage-api/python-search'
        final_response = requests.post(url=url_check, json=payload)
        result = json.loads(final_response.text)
        return result

# 返回格式： 200为未匹配到数据,返回为0的字段就是不存在的，需要录入到'api_check_200'表中     600为匹配到数据
#           "code":200,"msg":"success","result":
#                       {"league_id":"0",
#                       "league_name":"2020 LPL夏季赛",
#                       "team_a_id":"2663508672642",
#                       "team_a_name":"Snake WuDu",
#                       "team_b_id":"74",
#                       "team_b_name":"JDG电子竞技俱乐部"}
#                       }
#
# {
#           "code":600,"msg":"success","result":
#                       {"league_id":"268063888",
#                       "league_name":"2020 LPL夏季赛",
#                       "team_a_id":"2663508672642",
#                       "team_a_name":"Snake WuDu",
#                       "team_b_id":"74",
#                       "team_b_name":"JDG电子竞技俱乐部"}
#                       }


# 检测API返回为600的处理
def API_return_600(db, result, date_timestamp, insert_argument):
        # 检测为600, result['result']包含6个字段：
        # league_id, team_a_id, team_b_id,
        # league_name, team_a_name, team_b_name
        result_insert = result['result']
        league_id = result_insert['league_id']
        team_a_id = result_insert['team_a_id']
        team_b_id = result_insert['team_b_id']
        league_name = result_insert['league_name']
        team_a_name = result_insert['team_a_name']
        team_b_name = result_insert['team_b_name']
        type = insert_argument['type']
        status = insert_argument['status']
        bo = insert_argument['bo']
        team_a_score = insert_argument['team_a_score']
        team_b_score = insert_argument['team_b_score']
        check_match = insert_argument['check_match']
        win_team = insert_argument['win_team']
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
                             " team_a_id, team_a_name, team_a_score, team_b_id, team_b_name, " \
                             "team_b_score, league_name, check_match, win_team) VALUES ({0}, {1}, {2}," \
                             " {3}, {4}, {5}, '{6}', {7}, {8}, '{9}', {10}, '{11}', '{12}', " \
                             "'{13}');".format(type, league_id, status, date_timestamp, bo, team_a_id,
                                               team_a_name, team_a_score, team_b_id, team_b_name, team_b_score,
                                               league_name,
                                               check_match, win_team)
                print('600的未有记录执行插入：', sql_insert)
                db.update_insert(sql_insert)
                print('600的未有记录执行插入完成')
        else:
                print('600的有记录执行修改', type, status, bo, team_a_score, team_b_score, win_team,
                      check_match,
                      status_update_or_insert)
                db.update_by_id(type, status, bo, team_a_score, team_b_score, win_team, check_match,
                                status_update_or_insert)
                print('600的有记录执行修改完成')

# 检测API返回为200的处理
def API_return_200(db, result):
        insert_blacklist = result['result']
        league_name = insert_blacklist['league_name'] if insert_blacklist['league_id'] == 0 else 'Null'
        team_a_name = insert_blacklist['team_a_name'] if insert_blacklist['team_a_id'] == 0 else 'Null'
        team_b_name = insert_blacklist['team_b_name'] if insert_blacklist['team_b_id'] == 0 else 'Null'
        # api_check_200表去重插入
        distinct_asc = league_name + team_a_name + team_b_name
        distinct_desc = league_name + team_b_name + team_a_name
        sql_distinct = 'select id from api_check_200 where check_distinct in ("{}" ,"{}")'.format(distinct_asc, distinct_desc)
        sql_distinct_status = db.select_id(sql_distinct)
        # 确定表中无此记录
        if sql_distinct_status == None:
                # 添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                sql_blacklist = "INSERT INTO `api_check_200` (team_a_name, team_b_name, league_name, check_distinct) " \
                                "VALUES('{0}', '{1}', '{2}', '{3}');".format(team_a_name, team_b_name, league_name, distinct_asc)
                print('200的添加到api_check_200表中sql：', sql_blacklist)
                db.update_insert(sql_blacklist)
                print('200的添加到api_check_200表中sql完成')

