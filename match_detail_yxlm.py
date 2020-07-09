# -*-coding:utf-8-*-
import time
import requests
import json
from datetime import datetime, timedelta
from common_tool import get_response, redis_check
from lxml import etree
from common_tool import api_check
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_checkAPI

"""
尚牛电竞网比赛详情爬虫
"""

# 创建数据库对象
db = con_db()
# 创建redis对象
redis = RedisCache_checkAPI()


# LPL战队列表
LPL_list = [ 'RNG', 'ES', 'EDG', 'LGD', 'IG', 'BLG', 'TES', 'SN', 'WE',
             'OMG', 'DMO', 'LNG', 'JDG', 'FPX', 'RW', 'VG', 'V5']

headers = {
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

matchdetail_urlpre = 'https://www.shangniu.cn/live/lol/'
# 爬取规则： 拿到本周的startTime和endTime的时间戳组成访问赛程url,根据时间戳差值拿到上周的赛程url
# 过滤只保留LPL的赛程,拿到每个赛程的matchId,拼接得到对局详情url    https://www.shangniu.cn/live/lol/268063898
# 用xpath拿到对局详情url的battle_id,拼接对局详情数据的url        https://www.shangniu.cn/api/battle/lol/match/liveBattle?battleId=26806389801


# startTime为本周1的00:00:00   endTime为本周1的00:00:00
now_time = datetime.now()
# 判断今天星期几（周1到周日对应0到6）
judge_week = now_time.weekday()
start = now_time - timedelta(days=(judge_week))
last = start + timedelta(days=7)
start_str = start.strftime('%Y-%m-%d 00:00:00')
last_str = last.strftime('%Y-%m-%d 00:00:00')
start_date = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
last_date = datetime.strptime(last_str, '%Y-%m-%d %H:%M:%S')
startTime = int(start_date.timestamp()) * 1000
lastTime = int(last_date.timestamp()) * 1000

# 一周的时间戳差值为604800000
startTime_l = startTime - 604800000
lastTime_l = lastTime - 604800000
# 拼接本周的赛程url
url_matchlist = 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime, lastTime)

# print(url_matchlist)
# # 上周的赛程url
# url_matchlist_l= 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
#                 'lol&startTime={0}&endTime={1}'.format(startTime_l, lastTime_l)

# urls = [url_matchlist, url_matchlist_l]

def parse(url, headers):
    response_match = get_response(url, headers)
    response_match = response_match['body']
    # print('赛程个数和结果：', len(response_match), response_match)
    for response_each in response_match:
          team_a_name = response_each['teamAShortName']
          team_b_name = response_each['teamBShortName']
          teamAScore = response_each['teamAScore']
          teamBScore = response_each['teamBScore']
          status = response_each['status']
          # 过滤掉未进行的比赛
          if status != 0 and team_a_name in LPL_list and team_b_name in LPL_list:
                # print('enter this way')
                # 过滤只拿LPL的赛程,且比赛为已完成或者进行中的数据
                # 暂时不确定进行中的数据是否和已完成一样，要等下午对局开始在确定
                if team_a_name in LPL_list and team_b_name in LPL_list:
                      # print('过滤留下来的赛程队伍：', team_a_name, team_b_name)
                      matchId = response_each['matchId']
                      # 时间戳由毫秒转化为秒
                      matchTime = response_each['matchTime'][:-3]
                      leagueName = response_each['leagueName']
                      # 拼接对局详情url
                      matchdetail_url = matchdetail_urlpre + matchId
                      # print('对局详情url：', matchdetail_url)
                      # 请求对局详情url
                      requests.packages.urllib3.disable_warnings()
                      response_detail = requests.get(matchdetail_url, headers, verify=False)
                      response_detail = response_detail.text
                      html = etree.HTML(response_detail)

                      # 用xpath拿到对局详情页的battle_id,拼接对局详情数据的url,以及场次数
                      battle_id = str(html.xpath('/html/body/script[1]/text()'))
                      # print('拿到的battle_id：', battle_id)
                      battle_id_str = battle_id.split('battle_id:')[1]
                      battle_id = int(battle_id_str.split(',')[0])
                      # print('xpath拿到的battle_id：', battle_id)
                      # 根据两队总得分和battle_id拼接小场的详情数据url（有的时候默认进入是小场第一局，有的时候是最后一局，具体要看网站变动）
                      # 如果是进行中的赛事bo_count +1,因为当局还没计算出大比分,但已经可以进入对局详情页
                      bo_count = 0 if status == 1 else 1
                      battle_urls = {}
                      while bo_count <= (teamAScore + teamBScore):
                            battledetail_url = 'https://www.shangniu.cn/api/battle/lol/match/liveBattle?' \
                                               'battleId={}'.format(battle_id)
                            battle_urls[bo_count] = battledetail_url
                            battle_id += 1
                            bo_count += 1
                      # print('battle_urls:', battle_urls)
                      parse_detail(battle_urls, leagueName, team_a_name, team_b_name, matchTime)


# 解析对局详情的url,录入到数据库,录入的是赛事对应的小场
# url_list对应的{小局第几场：场次的详情url，...}
def parse_detail(url_list, leagueName, team_a_name, team_b_name, matchTime):
      # redis中加入网站源标记
      source = 'SN'
      result = redis_check(redis, db, source, leagueName, team_a_name, team_b_name, matchTime)
      # 如果match_id为空，说明尚牛的赛事详情赛程在赛程表中没找到，这时不录入
      if result:
          match_id = result[0]
          # 收集详情数据并写入数据库
          for key, value_url in url_list.items():
               response = get_response(value_url, headers)['body']
               # print('body:', response)
               if response !={} and match_id :
                   # print('源详情url：', value_url)
                   status = response['status']
                   index_num = response['index']
                   duration = response['duration']
                   source_matchid = response['battle_id']   # 源网站的赛事id
                   economic_diff = response['economic_diff']
                   economic_diff = str(economic_diff)
                   economic_diff = json.dumps(economic_diff)
                   # print('经济差为：', type(economic_diff), economic_diff)
                   types = 1    # 默认为英雄联盟
                   # A,B队的英雄列表要自己拼接
                   team_a_hero = []
                   team_b_hero = []
                   # 判断response['team_stats'][0]为A队
                   if response['team_stats'][0]['team_short_name'] == team_a_name:
                       team_stats_0 = response['team_stats'][0]
                       team_stats_1 = response['team_stats'][1]
                   else:
                       team_stats_1 = response['team_stats'][0]
                       team_stats_0 = response['team_stats'][1]
                   team_a_kill_count = team_stats_0['kill_count']
                   team_b_kill_count = team_stats_1['kill_count']
                   team_a_death_count = team_stats_0['death_count']
                   team_b_death_count = team_stats_1['death_count']
                   team_a_assist_count = team_stats_0['assist_count']
                   team_b_assist_count = team_stats_1['assist_count']
                   team_a_big_dragon_count = team_stats_0['big_dragon_count']
                   team_b_big_dragon_count = team_stats_1['big_dragon_count']
                   team_a_small_dragon_count = team_stats_0['small_dragon_count']
                   team_b_small_dragon_count = team_stats_1['small_dragon_count']
                   team_a_tower_count = team_stats_0['tower_success_count']
                   team_b_tower_count = team_stats_0['tower_success_count']
                   win_team = 'A' if team_stats_0['is_win'] == 'true' else 'B'
                   first_big_dragon_team = 'A' if team_stats_0['is_first_big_dragon'] == True else 'B'
                   first_small_dragon_team = 'A' if team_stats_0['is_first_small_dragon'] == True else 'B'
                   first_blood_team = 'A' if team_stats_0['is_first_blood'] == True else 'B'
                   team_a_five_kills = '1' if team_stats_0['is_five_kills'] == True else '0'
                   team_b_five_kills = '1' if team_stats_1['is_five_kills'] == True else '0'
                   team_a_ten_kills = '1' if team_stats_0['is_ten_kills'] == True else '0'
                   team_b_ten_kills = '1' if team_stats_1['is_ten_kills'] == True else '0'
                   first_tower_team = 'A' if team_stats_0['is_ten_kills'] == True else 'B'
                   team_a_money = team_stats_0['money']
                   team_b_money = team_stats_1['money']
                   pick_list_A = team_stats_0['pick_list']
                   pick_list_B = team_stats_1['pick_list']
                   # print('两个战队的名字：',team_stats_0['team_name'], team_stats_1['team_name'])
                   for pick_list in  pick_list_A:
                       team_a_hero.append(pick_list['avatar'])
                   for pick_list in  pick_list_B:
                       team_b_hero.append(pick_list['avatar'])
                   team_a_hero = str(team_a_hero)
                   team_b_hero = str(team_b_hero)
                   team_a_side = team_stats_0['side']
                   team_b_side = team_stats_1['side']
                   player_messages = response['player_stats']
                   for player_message in player_messages:
                       # print('选手的信息:', player_message)
                       player_id = player_message['player_id']
                       player_name = player_message['player_name']
                       player_avatar = player_message['player_avatar']
                       hero_id = player_message['hero_id']
                       hero_level = player_message['hero_level']
                       hero_name = player_message['hero_name']
                       hero_avatar = player_message['hero_avatar']
                       kill_count = player_message['kill_count']
                       death_count = player_message['death_count']
                       assist_count = player_message['assist_count']
                       # last_hit_count和last_hit_minute赛后才返回
                       last_hit_count = player_message['last_hit_count'] if status !=0 else 0
                       last_hit_minute = 0
                       damage_count = player_message['damage_count'] if status !=0 else 0
                       damage_minute = 0
                       damage_percent = 0
                       damage_taken_count = player_message['damage_taken_count'] if status !=0 else 0
                       damage_taken_minute = 0
                       damage_taken_percent = 0
                       kda = player_message['kda'] if status !=0 else 0
                       money_count = player_message['money_count'] if status !=0 else 0
                       money_minute = 0
                       offered_rate = 0
                       score = 0
                       equip_ids = player_message['equip_ids']
                       skill_ids = player_message['skill_ids']
                       # 位置可能为空
                       position = player_message['player_position']
                       team_id = player_message['team_id']

                       # 添加或修改选手对局记录
                       sql_player_insert = "INSERT INTO `game_player_battle_record` (match_id, player_id, player_name, " \
                        "player_avatar, hero_id, hero_level, hero_name, hero_avatar, kill_count, death_count, assist_count," \
                        " last_hit_count, last_hit_minute, damage_count, damage_minute, damage_percent, damage_taken_count, " \
                        "damage_taken_minute, damage_taken_percent, kda, money_count, money_minute, offered_rate, score, " \
                        "equip_ids, skill_ids, position, type, source_matchid, team_id) VALUES({0}, '{1}', '{2}', '{3}', {4}, {5}, '{6}', '{7}'," \
                        " {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23}, " \
                        "'{24}', '{25}', '{26}', {27}, '{28}', {29}) " \
                        "ON DUPLICATE KEY UPDATE player_name = '{2}', player_avatar = '{3}', " \
                        "hero_id = {4}, hero_level = {5}, hero_name = '{6}', hero_avatar = '{7}', kill_count = {8}, " \
                        "death_count = {9}, assist_count = {10}, last_hit_count = {11}, last_hit_minute = {12}, " \
                        "damage_count = {13}, damage_minute = {14}, damage_percent = {15}, damage_taken_count = {16}, " \
                        "damage_taken_minute = {17}, damage_taken_percent = {18}, kda = {19}, money_count = {20}, " \
                        "money_minute = {21}, offered_rate = {22}, score = {23}, equip_ids = '{24}', skill_ids = '{25}'," \
                        " position ='{26}', type = {27}, source_matchid = '{28}', team_id={29};".format(match_id, player_id, player_name, player_avatar, hero_id,
                        hero_level, hero_name, hero_avatar, kill_count, death_count, assist_count, last_hit_count,
                        last_hit_minute, damage_count, damage_minute, damage_percent, damage_taken_count,
                        damage_taken_minute, damage_taken_percent, kda, money_count, money_minute, offered_rate, score,
                        equip_ids, skill_ids, position, types, source_matchid, team_id)
                       # print('记录选手表：', sql_player_insert)
                       db.update_insert(sql_player_insert)
                       # print('记录选手表插入完成')

                   # print('得到的match_id和index_num：',match_id, index_num)
                   # 添加或修改对局详情记录
                   sql_battle_insert = "INSERT INTO `game_match_battle` (match_id, duration, index_num, economic_diff," \
                   " status, type, team_a_kill_count, team_b_kill_count, team_a_death_count, team_b_death_count, " \
                   "team_a_assist_count, team_b_assist_count, team_a_big_dragon_count, team_b_big_dragon_count, " \
                   "team_a_small_dragon_count, team_b_small_dragon_count, team_a_tower_count, team_b_tower_count, win_team, " \
                   "first_big_dragon_team, first_small_dragon_team, first_blood_team, team_a_five_kills, team_b_five_kills, " \
                   "team_a_ten_kills, team_b_ten_kills, first_tower_team, team_a_money, team_b_money, team_a_hero, team_b_hero, " \
                   "team_a_side, team_b_side, source_matchid) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, " \
                   "{13}, {14}, {15}, {16}, {17}, '{18}', '{19}', '{20}', '{21}', '{22}', '{23}', '{24}', '{25}', '{26}'," \
                   " {27}, {28}, \"{29}\", \"{30}\", '{31}', '{32}', '{33}') ON DUPLICATE KEY UPDATE duration = {1}, " \
                   "economic_diff = {3}, status = {4}, type = {5}, team_a_kill_count = {6}, team_b_kill_count = {7}, " \
                   "team_a_death_count = {8}, team_b_death_count = {9}, team_a_assist_count = {10}, team_b_assist_count = {11}, " \
                   "team_a_big_dragon_count = {12}, team_b_big_dragon_count = {13}, team_a_small_dragon_count = {14}, " \
                   "team_b_small_dragon_count = {15}, team_a_tower_count = {16}, team_b_tower_count = {17}, " \
                   "win_team = '{18}', first_big_dragon_team = '{19}', first_small_dragon_team = '{20}', " \
                   "first_blood_team = '{21}', team_a_five_kills = '{22}', team_b_five_kills = '{23}', team_a_ten_kills = '{24}'," \
                   "team_b_ten_kills = '{25}', first_tower_team = '{26}', team_a_money = {27}, team_b_money = {28}, " \
                   "team_a_hero = \"{29}\", team_b_hero = \"{30}\", team_a_side = '{31}', team_b_side = '{32}', source_matchid ='{33}';".format(
                   match_id, duration, index_num, economic_diff, status, types, team_a_kill_count, team_b_kill_count,
                   team_a_death_count, team_b_death_count, team_a_assist_count, team_b_assist_count, team_a_big_dragon_count,
                   team_b_big_dragon_count, team_a_small_dragon_count, team_b_small_dragon_count, team_a_tower_count,
                   team_b_tower_count, win_team, first_big_dragon_team, first_small_dragon_team, first_blood_team,
                   team_a_five_kills, team_b_five_kills, team_a_ten_kills, team_b_ten_kills, first_tower_team, team_a_money,
                   team_b_money, team_a_hero, team_b_hero, team_a_side, team_b_side, source_matchid)
                   # print('记录对局详情表：', sql_battle_insert)
                   db.update_insert(sql_battle_insert)
                   # print('记录对局详情表插入完成')


parse(url_matchlist, headers)
