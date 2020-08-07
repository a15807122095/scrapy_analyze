# -*-coding:utf-8-*-
import requests
import json
import time
from datetime import datetime, timedelta
import logging
import sys

# 生成一个log,log级别为ERROR，用来打印调试和记录异常的log文件
def get_log(log_name, level=logging.ERROR):
        log_object = logging.getLogger(log_name)
        log_object.setLevel(level)
        # 规定log输出的格式
        formatter = logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
        # 设置handler的控制台输出属性
        StreamHandler = logging.StreamHandler(sys.stdout)
        StreamHandler.setFormatter(formatter)
        # 给logger对象添加handler文件输出属性
        log_object.addHandler(StreamHandler)
        # 设置handler的文件输出属性
        filehandler = logging.FileHandler('./Log/%s.log' % (log_name))
        filehandler.setFormatter(formatter)
        # 给logger对象添加handler文件输出属性
        log_object.addHandler(filehandler)
        return log_object


# 使用代理抓取,从proxies.txt中找到有效的代理，从第一个ip开始，设置7s延时，失败继续取
def get_response_proxy(url, headers):
        for line in open("proxies.txt"):
                # 构造代理
                line = line.rstrip('\n')
                proxies = {'https':line}
                # print(proxies)
                try:
                        response = requests.get(url=url, headers=headers, proxies=proxies, timeout=7)
                        response_text = response.text
                        response_json = json.loads(response_text)
                        return response_json
                except Exception:
                        continue


# 本机ip使用request
def get_response(url, headers):
        response = requests.get(url=url, headers=headers)
        response_text = response.text
        response_json = json.loads(response_text)
        return response_json

# 本机ip使用post
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
        url_check = 'http://api.saishikong.com/data/backstage-api/python-search'
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


def league_check(league_name, type):
        payload_league = {
                'league_name': league_name,
                'type': type,
        }
        url_league = 'http://api.saishikong.com/data/backstage-api/matching-league'
        final_response = requests.post(url=url_league, json=payload_league)
        result = json.loads(final_response.text)
        return result
# 返回格式：
# {'code': 600, 'msg': 'success', 'result': {
#               'league_id': '268063485',
#               'league_name': '2020 LCK夏季赛'
#               }
#    }


def team_check(team_name, type):
        payload_team = {
                'team_name': team_name,
                'type': type,
        }
        url_league = 'http://api.saishikong.com/data/backstage-api/matching-team'
        final_response = requests.post(url=url_league, json=payload_team)
        result = json.loads(final_response.text)
        return result
# 返回格式： {'code': 600, 'msg': 'success', 'result': {
#                       'team_id': '672',
#                       'team_name': 'OMD战队'
#                       }
# }

def player_check(player_name, type):
        payload_team = {
                'name': player_name,
                'type': type,
        }
        url_league = 'http://api.saishikong.com/data/backstage-api/matching-player'
        final_response = requests.post(url=url_league, json=payload_team)
        result = json.loads(final_response.text)
        return result
# 返回格式： {'code': 600, 'msg': 'success', 'result': {
#                       'player_id': '186',
#                       'player_name': 'doinb'
#                       }
# }

def hero_check(hero_name, type):
        payload_team = {
                'name': hero_name,
                'type': type,
        }
        url_league = 'http://api.saishikong.com/data/backstage-api/matching-hero'
        final_response = requests.post(url=url_league, json=payload_team)
        result = json.loads(final_response.text)
        return result
# 返回格式： {'code': 600, 'msg': 'success', 'result': {
#                       'hero_id': '33',
#                       'hero_name': '巨魔之王'
#                       }
# }


# 从有联赛名,对战双方的赛程检测API返回为200的处理(记录到旧的黑名单表：api_check_200)
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


# 只有联赛名，或战队名检测添加到黑名单(记录到新的黑名单表：black_list)
def api_return_200(sql_check, sql_insert, db):
        blacklist_id = db.select_id(sql_check)
        # 黑名单未添加才记录
        if not blacklist_id:
                db.update_insert(sql_insert)

# 得到一天中剩下的大致时间戳
def fullday_remain(now_time):
        now_stamp = now_time.timestamp()
        fullday_time = now_time.strftime('%Y-%m-%d 23:59:55')
        fullday_time = datetime.strptime(fullday_time, '%Y-%m-%d %H:%M:%S')
        fullday_time = fullday_time.timestamp()
        return fullday_time - now_stamp

#得到上周的日期和这周到今天的日期字符串列表：
# ['2020.07.20', '2020.07.21', '2020.07.22', '2020.07.23', '2020.07.24', '2020.07.25', '2020.07.26', '2020.07.27']
def get_weeks():
        week_str = []
        now = datetime.now().date()
        num = 7 + now.weekday() + 1
        for i in range(num):
            now_str = now.strftime('%Y.%m.%d')
            week_str.append(now_str)
            now -= timedelta(days=1)
        return week_str

# 有赛程id的表都会有一个匹配过程：
# 先去redis中找，如果找到说明之前已经访问过，直接拿到赛事id
# 如果没找到就访问后端api拿到赛程信息，再从game_python_match表中拿赛程id
# 没拿到过滤掉，拿到后写入redis缓存
# 保存到redis，设置1天的过期时间
# 格式为：str（ 源网站 + 源网站的赛事id) : str（源网站+主键 + league_id + team_a_id + team_b_id + team_a_name + team_b_name + league_name）
def redis_check(redis, game_name, db, source, leagueName, source_matchid, source_a_name, source_b_name, matchTime):
        redis_key = source + source_matchid
        redis_value = redis.get_data(redis_key)
        # print('redis中的存储情况：', redis_key, redis_value)
        if redis_value:
                result = redis_value.split(source)[1]
                # print(111, result)
                results = result.split('+')
                # print(222, results)
                match_id = results[0]
                league_id = results[1]
                team_a_id = results[2]
                tea_b_id = results[3]
                team_a_name = results[4]
                tea_b_name = results[5]
                league_name = results[6]
                return match_id, league_id, team_a_id, tea_b_id, team_a_name, tea_b_name, league_name
        else:
                # redis没记录，请求检测接口
                # print('检验的参数:', game_name, leagueName, source_a_name, source_b_name)
                result = api_check(game_name, leagueName, source_a_name, source_b_name)
                # print('返回的api接口：', result)
                if result['code'] == 600:
                        league_id = result['result']['league_id']
                        team_a_id = result['result']['team_a_id']
                        team_b_id = result['result']['team_b_id']
                        team_a_name = result['result']['team_a_name']
                        team_b_name = result['result']['team_b_name']
                        league_name = result['result']['league_name']
                        # 尚牛和雷竞技的比赛时间与官网有差别，用源网的时间左右一个小时过滤官网的时间来查找赛事id
                        # 其它网站的比赛时间暂时还不清楚，后面再加条件区分
                        matchTime_before = int(matchTime) - 3600
                        matchTime_after = int(matchTime) + 3600
                        sql_check = 'select id from game_python_match where league_id = {0} ' \
                        'and team_a_id in ({1}, {2}) and team_b_id in ({1}, {2}) and start_time between {3} and {4};'.\
                        format(league_id, team_a_id, team_b_id, matchTime_before, matchTime_after)
                        # print('检测api返回拼凑的sql：', sql_check)
                        # 拿到数据再去赛程表拿到赛事id（未拿到赛事id的暂时不处理）
                        match_id = db.select_id(sql_check)
                        # print('匹配到的match_id:', match_id)
                        if match_id:
                                # 保存到redis，设置1天的过期时间
                                # 格式为：str（ 源网站 + 源网站的赛事id) : str（源网站+主键 + league_id + team_a_id + team_b_id +
                                # team_a_name + team_b_name）
                                # print('存入redis')
                                redis_value = source + str(match_id) + '+' + str(league_id) + '+' + \
                                              str(team_a_id)+ '+' + str(team_b_id) + '+' + str(team_a_name)+ \
                                              '+' + str(team_b_name) + '+' + str(league_name)
                                redis.set_data(redis_key, 86400, redis_value)
                                # print('已经保存到redis')
                        return match_id, league_id, team_a_id, team_b_id, team_a_name, team_b_name, league_name

                if result['code'] == 200:
                        # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                        API_return_200(db, result)
                        return None

# 匹配选手id:
# 先去redis中找，如果找到说明之前已经访问过，直接拿到player_id
# 如果没找到就访问后端api拿到player_id
# 没拿到过滤掉，拿到后写入redis缓存
# 保存到redis，设置1天的过期时间
# 格式为：str（ 源网站 + 源网站的player_name) : str（源网站+player_id）
def redis_check_playerID(player_name, source, redis, types, league_name, db):
        # 先从redis中找到player_id，有记录代表之前已记录,取出player
        # redis存储结构：（源+player+player_name:player_id）‘score+player+uzi:'123'
        key_player = source + '+' + 'player' + '+' + player_name
        result = redis.get_data(key_player)
        # print('redis查询player的结果：', result)
        if result:
                # print('redis有记录：', result)
                return result
        else:
                # print('redis中没记录：', result)
                # redis中不存在就访问后端接口
                result_player = player_check(player_name, types)
                # print('访问后端拿到的选手信息：', result_player)
                if result_player['code'] == 600:
                        player_id = result_player['result']['player_id']
                        # 记录到redis中，格式为：（源+player+source_player_id:player_id）‘score+player+8377:'123'
                        redis.set_data(key_player, 86400, player_id)
                        # print('redis记录player完成：',key_player, player_id)
                        return player_id
                else:
                        # 记录到黑名单中的选手名称
                        sql_blacklist = "select id from black_list where player_name ='{}';".format(player_name)
                        sql_add_blacklist = "insert into black_list set league_name = '{0}',player_name ='{1}', " \
                                            "source_from = 1, judge_position=0010;".format(league_name, player_name)
                        # print('记录到选手黑名单sql:', sql_add_blacklist)
                        api_return_200(sql_blacklist, sql_add_blacklist, db)
                        return None





# 赛程爬虫根据redis_check进行更新或者插入操作
def redis_return_operation(redis, game_name, db, source_from, league_sourcename, source_matchId, team_a_sourcename, team_b_sourcename, start_time,
                           types, team_a_score, team_b_score, status, bo, win_team, propertys):
        # 先检查redis是否有记录
        result = redis_check(redis, game_name, db, source_from, league_sourcename, source_matchId,
                             team_a_sourcename, team_b_sourcename, start_time)
        match_id = result[0] if result else None
        league_id = result[1] if result else None
        team_a_id = result[2] if result else None
        team_b_id = result[3] if result else None
        team_a_name = result[4] if result else None
        team_b_name = result[5] if result else None
        league_name = result[6] if result else None
        # print('redis返回的数据：',result)
        # 后端返回600且match_id不为空,拿到match_id更新其他字段（其中比分要判断：以a,b队比分之和大的为准）
        if result and match_id:
                sql_score = 'select team_a_score, team_b_score from game_python_match where id = {};'.format(
                        match_id)
                result_score = db.select_all(sql_score)
                # 以比分大的为准
                team_a_score = int(team_a_score)
                team_b_score = int(team_b_score)
                if team_a_score < result_score[0]:
                        team_a_score = result_score[0]
                if team_b_score < result_score[1]:
                        team_b_score = result_score[1]
                db.update_by_id(types, status, bo, team_a_score, team_b_score, win_team, propertys, source_from,
                                source_matchId, start_time, match_id)
        # 后端返回600但match_id为空,说明赛程表没有这场赛程，直接插入
        if result and not match_id:
                sql_insert = "INSERT INTO `game_python_match` (type, league_id, status, start_time, bo," \
                             " team_a_id, team_a_name, team_a_score, team_b_id, team_b_name, " \
                             "team_b_score, league_name, propertys, source_from, source_matchId, win_team) VALUES ({0}, {1}, {2}," \
                             " {3}, {4}, {5}, '{6}', {7}, {8}, '{9}', {10}, '{11}', '{12}', '{13}', '{14}', " \
                             "'{15}');".format(types, league_id, status, start_time, bo, team_a_id,
                                               team_a_name, team_a_score, team_b_id, team_b_name, team_b_score,
                                               league_name, propertys, source_from, source_matchId,
                                               win_team)
                # print('600的未有记录执行插入：', sql_insert)
                db.update_insert(sql_insert)
                # print('600的未有记录执行插入完成')

# 校验后端返回的数据，并存入redis中
def redis_check_data(redis, source, data):
        # print('key:', data)
        redis_key = source + data
        redis_value = redis.get_data(redis_key)
        # print('redis中的存储情况：', redis_key, redis_value)
        if redis_value:
                return redis_value
        else:
                return None

# 将两个字典合并到字典1，键相同值相加，键不同值保留，并返回字典1
def merge_dict(dict_one,dict_two):
        for key, value in dict_two.items():
                if key in dict_one:
                        dict_one[key] += value
                else:
                        dict_one[key] = value
        return dict_one


