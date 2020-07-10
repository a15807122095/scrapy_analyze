# -*-coding:utf-8-*-
import requests
import json
import time
from datetime import datetime, timedelta

def get_response(url, headers):
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url=url, headers=headers, verify=False)
        response_text = response.text
        response_json = json.loads(response_text)
        return response_json

def post_response(url, data, headers):
        response = requests.post(url=url, data=data, headers=headers)
        response = response.text
        result = json.loads(response)
        return result


# # 访问接口前先在表中用网站源的match_id字段匹配一下，有就不再访问接口
def check_local(db, source_matchId):
        sql_check = 'select id from game_python_match where source_matchId = "{}"'.format(source_matchId)
        # print('访问接口前的sql：', sql_check)
        status_check = db.select_id(sql_check)
        # print('访问接口前的拼接字符串和匹配到的主键：', status_check, check_match)
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
        propertys = insert_argument['propertys']
        source_from = insert_argument['source_from']
        source_matchId = insert_argument['source_matchId']
        # 将result_insert和date_timestamp与game_python_match进行对比确定是否有这场赛事
        sql_check = "select id from game_python_match where source_matchId = '{}';".format(source_matchId)
        # print('600的查询主键sql：', sql_check)
        status_update_or_insert = db.select_id(sql_check)
        # print('600的查询主键：', status_update_or_insert)
        if status_update_or_insert == None:
                # 确定没有这场赛事就执行插入数据
                # 拿到其余需要更新的字段
                sql_insert = "INSERT INTO `game_python_match` (type, league_id, status, start_time, bo," \
                             " team_a_id, team_a_name, team_a_score, team_b_id, team_b_name, " \
                             "team_b_score, league_name, check_match, propertys, source_from, source_matchId, win_team) VALUES ({0}, {1}, {2}," \
                             " {3}, {4}, {5}, '{6}', {7}, {8}, '{9}', {10}, '{11}', '{12}', '{13}', '{14}', '{15}', " \
                             "'{16}');".format(type, league_id, status, date_timestamp, bo, team_a_id,
                                               team_a_name, team_a_score, team_b_id, team_b_name, team_b_score,
                                               league_name, check_match, propertys, source_from, source_matchId, win_team)
                # print('600的未有记录执行插入：', sql_insert)
                db.update_insert(sql_insert)
                # print('600的未有记录执行插入完成')
        else:
                # print('600的有记录执行修改', type, status, bo, team_a_score, team_b_score, win_team,
                #       check_match,
                #       status_update_or_insert)
                db.update_by_id(type, status, bo, team_a_score, team_b_score, win_team, check_match, propertys,
                                source_from, source_matchId, status_update_or_insert)
                # print('600的有记录执行修改完成')

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
                # print('200的添加到api_check_200表中sql：', sql_blacklist)
                db.update_insert(sql_blacklist)
                # print('200的添加到api_check_200表中sql完成')


# 得到一天中剩下的大致时间戳
def fullday_remain(now_time):
        now_stamp = now_time.timestamp()
        fullday_time = now_time.strftime('%Y-%m-%d 23:59:55')
        fullday_time = datetime.strptime(fullday_time, '%Y-%m-%d %H:%M:%S')
        fullday_time = fullday_time.timestamp()
        return fullday_time - now_stamp

#得到今日日期字符串：
# '2020.06.29'， '2020.06.30'， '2020.07.01'， '2020.07.02'， '2020.07.03'， '2020.07.04'， '2020.07.05'
def get_weeks():
        week_str = []
        num = 1
        now = datetime.now().date()
        while num <= 7:
                now_str = now.strftime('%Y.%m.%d')
                week_str.append(now_str)
                now += timedelta(days=1)
                num += 1
        return week_str

# 有赛程id的表都会有一个匹配过程：
# 先去redis中找，如果找到说明之前已经访问过，直接拿到赛事id
# 如果没找到就访问后端api拿到赛程信息，再从game_python_match表中拿赛程id
# 没拿到过滤掉，拿到后写入redis缓存
# 保存到redis，设置1天的过期时间
# 格式为：str（ 源网站 + 源数据联赛名 + 源数据A队名 + 源数据B队名 + 比赛时间) : str（源网站+主键）'+'str（a队id）'+' str（b队id）
def redis_check(redis, db, source, leagueName, source_a_name, source_b_name, matchTime):
        redis_key = source + leagueName + source_a_name + source_b_name + matchTime
        redis_value = redis.get_data(redis_key)
        # print('redis中的存储情况：', redis_key, redis_value)
        if redis_value:
                result = redis_value.split(source)[1]
                results = result.split('+')
                match_id = results[0]
                team_a_id = results[1]
                tea_b_id = results[2]
                return match_id, team_a_id, tea_b_id
        else:
                # redis没记录，请求检测接口
                game_name = '英雄联盟'
                result = api_check(game_name, leagueName, source_a_name, source_b_name)
                # print('返回的api接口：', result)
                if result['code'] == 600:
                        league_id = result['result']['league_id']
                        team_a_id = result['result']['team_a_id']
                        team_b_id = result['result']['team_b_id']
                        # 尚牛和雷竞技的比赛时间与官网有差别，用源网的时间左右一个小时过滤官网的时间来查找赛事id
                        # 其它网站的比赛时间暂时还不清楚，后面再加条件区分
                        matchTime_before = int(matchTime) - 3600
                        matchTime_after = int(matchTime) + 3600
                        sql_check = 'select id from game_python_match where league_id = {0} and team_a_id in ({1}, {2})' \
                        ' and team_b_id in ({1}, {2}) and start_time between {3} and {4};'.format(league_id, team_a_id,
                                                                                     team_b_id, matchTime_before,
                                                                                     matchTime_after)
                        # print('检测api返回拼凑的sql：', sql_check)
                        # 拿到数据再去赛程表拿到赛事id（未拿到赛事id的暂时不处理）
                        match_id = db.select_id(sql_check)
                        # print('匹配到的match_id:', match_id)
                        if match_id != None:
                                # 保存到redis，设置1天的过期时间
                                # 格式为：str（ 源网站 + 源数据联赛名 + 源数据A队名 + 源数据B队名 + 比赛时间) : str（源网站+主键）'+'
                                # str（a队id）'+' str（b队id）
                                # print('存入redis')
                                redis_value = source + str(match_id) + '+' + str(team_a_id) + '+' + str(team_b_id)
                                redis.set_data(redis_key, 86400, redis_value)
                                # print('已经保存到redis')
                        return match_id, team_a_id, team_b_id

                if result['code'] == 200:
                        # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                        API_return_200(db, result)
                        return None
