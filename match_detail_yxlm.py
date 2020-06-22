# -*-coding:utf-8-*-
import time
import requests
from datetime import datetime, timedelta
from common_tool import get_response
from setting import headers_yxlmgw
from lxml import etree
from common_tool import api_check
from import_data_to_mysql import con_db

"""
尚牛电竞网爬虫
"""

# LPL战队列表
LPL_list = [ 'RNG', 'ES', 'EDG', 'LGD', 'IG', 'BLG', 'TES', 'SN', 'WE',
             'OMG', 'OMD', 'LNG', 'JDG', 'FPX', 'RW', 'VG', 'V5']

position_list = {'上单':1, '打野':2, '中单':3, 'ADC':4, '辅助':5}

matchdetail_urlpre = 'https://www.shangniu.cn/live/lol/'
# 爬取规则： 拿到本周的startTime和endTime的时间戳组成访问赛程url,根据时间戳差值拿到上周的赛程url
# 过滤只保留LPL的赛程,拿到每个赛程的matchId,拼接得到对局详情url    https://www.shangniu.cn/live/lol/268063898
# 用xpath拿到对局详情url的battle_id,拼接对局详情数据的url        https://www.shangniu.cn/api/battle/lol/match/liveBattle?battleId=26806389801

# startTime为本周1的00:00:00   endTime为本周1的00:00:00
now_time = datetime.now()
# 判断今天星期几（周1到周日对应0到6）
judge_week = now_time.weekday()
print(now_time)
start = now_time - timedelta(days=(judge_week))
last = start + timedelta(days=7)
start_str = start.strftime('%Y-%m-%d 00:00:00')
last_str = last.strftime('%Y-%m-%d 00:00:00')
start_date = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
last_date = datetime.strptime(last_str, '%Y-%m-%d %H:%M:%S')
startTime = int(start_date.timestamp()) * 1000
lastTime = int(last_date.timestamp()) * 1000
# print(startTime, lastTime)

# 拼接本周的赛程url
url_matchlist = 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime, lastTime)
# 一周的时间戳差值为604800000
startTime_l = startTime - 604800000
lastTime_l = lastTime - 604800000
# 上周的赛程url
url_matchlist_l= 'https://www.shangniu.cn/api/battle/index/matchList?gameType=' \
                'lol&startTime={0}&endTime={1}'.format(startTime_l, lastTime_l)
# print(url_matchlist, '\n', url_matchlist_l)

urls = [url_matchlist, url_matchlist_l]

def parse(url):
    now_1 = time.time()
    response_match = get_response(url, headers_yxlmgw)
    response_match = response_match['body']
    print('赛程个数和结果：', len(response_match), response_match)
    for response_each in response_match:
          team_a_name = response_each['teamAShortName']
          team_b_name = response_each['teamBShortName']
          teamAScore = response_each['teamAScore']
          teamBScore = response_each['teamBScore']
          status = response_each['status']
          # 过滤掉未进行的比赛
          if status != 0 and team_a_name in LPL_list and team_b_name in LPL_list:
                print('enter this way')
                # 过滤只拿LPL的赛程,且比赛为已完成或者进行中的数据
                # 暂时不确定进行中的数据是否和已完成一样，要等下午对局开始在确定
                if team_a_name in LPL_list and team_b_name in LPL_list:
                      # print('过滤留下来的赛程队伍：', team_a_name, team_b_name, bo, type(bo))
                      matchId = response_each['matchId']
                      matchTime = response_each['matchTime']
                      leagueName = response_each['leagueName']
                      # 拼接对局详情url
                      matchdetail_url = matchdetail_urlpre + matchId
                      # print('对局详情url：', matchdetail_url)
                      # 请求对局详情url
                      requests.packages.urllib3.disable_warnings()
                      response_detail = requests.get(matchdetail_url, headers_yxlmgw, verify=False)
                      response_detail = response_detail.text
                      html = etree.HTML(response_detail)

                      # 用xpath拿到对局详情页的battle_id,拼接对局详情数据的url,以及场次数
                      battle_id = str(html.xpath('/html/body/script[1]/text()'))
                      print('html源数据：', battle_id)
                      battle_id_str = battle_id.split('battle_id:')[1]
                      battle_id = int(battle_id_str.split(',')[0])
                      # print('xpath拿到的battle_id：', battle_id)
                      # 根据两队总得分和battle_id拼接小场的详情数据url（因为默认进入小场最后一局,需要推算出第一句的url）
                      bo_count = teamAScore + teamBScore
                      # 如果是进行中的赛事bo_count +1,因为当局还没计算出大比分,但已经可以进入对局详情页
                      if status == 1:
                          bo_count += 1
                      battle_urls = {}
                      while bo_count > 0:
                            battledetail_url = 'https://www.shangniu.cn/api/battle/lol/match/liveBattle?' \
                                               'battleId={}'.format(battle_id)
                            battle_urls[bo_count] = battledetail_url
                            battle_id -= 1
                            bo_count -= 1
                            result = parse_detail(battle_urls, team_a_name, team_b_name, matchTime, leagueName)
                      print(battle_urls)
    now_2 = time.time()
    print(now_2 - now_1)

# 解析对局详情的url,录入到数据库,录入的是赛事对应的小场
def parse_detail(url_list, leagueName, team_a_name, team_b_name, matchTime):
      # 创建数据库对象,请求检测接口拿到规范的队伍名称，在匹配赛事id
      db = con_db()
      # 请求检测接口
      game_name = '英雄联盟'
      result = api_check(game_name, leagueName, team_a_name, team_b_name, matchTime)
      for key, value_url in url_list.items():
           index_num = key
           response = get_response(value_url, headers_yxlmgw)['body']
           duration = response['duration']
           economic_diff = response['economic_diff']
           status = response['status']
           type = 1    # 默认为英雄联盟
           print(index_num)
           print(duration)
           print(economic_diff)
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
           team_a_big_dragon_count = team_stats_1['big_dragon_count']
           team_a_small_dragon_count = team_stats_0['small_dragon_count']
           team_b_small_dragon_count = team_stats_1['small_dragon_count']
           team_a_tower_count = team_stats_0['tower_success_count']
           team_b_tower_count = team_stats_0['tower_success_count']
           win_team = 'A' if team_stats_0['is_win'] == 'true' else 'B'
           first_big_dragon_team = 'A' if team_stats_0['is_first_big_dragon'] == 'true' else 'B'
           first_small_dragon_team = 'A' if team_stats_0['is_first_small_dragon'] == 'true' else 'B'
           first_blood_team = 'A' if team_stats_0['is_first_blood'] == 'false' else 'B'
           team_a_five_kills = '0' if team_stats_0['is_five_kills'] == 'false' else '1'
           team_b_five_kills = '0' if team_stats_1['is_five_kills'] == 'false' else '1'
           team_a_ten_kills = '0' if team_stats_0['is_ten_kills'] == 'false' else '1'
           team_b_ten_kills = '0' if team_stats_1['is_ten_kills'] == 'false' else '1'
           first_tower_team = 'A' if team_stats_0['is_ten_kills'] == 'true' else 'B'
           team_a_money = team_stats_0['money']
           team_b_money = team_stats_1['money']
           pick_list_A = team_stats_0['pick_list']
           pick_list_B = team_stats_1['pick_list']
           for pick_list in  pick_list_A:
               team_a_hero.append(pick_list['avater'])
           for pick_list in  pick_list_B:
               team_b_hero.append(pick_list['avater'])
           team_a_hero = str(team_a_hero)
           team_b_hero = str(team_b_hero)
           team_a_side = team_stats_0['side']
           team_b_side = team_stats_1['side']
           player_messages = response['player_stats']
           for player_message in player_messages:
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
               last_hit_count = player_message['last_hit_count']
               last_hit_minute = player_message['last_hit_minute']
               damage_count = player_message['damage_count']
               damage_minute = player_message['damage_minute']
               damage_percent = player_message['damage_percent']
               damage_taken_count = player_message['damage_taken_count']
               damage_taken_minute = player_message['damage_taken_minute']
               damage_taken_percent = player_message['damage_taken_percent']
               kda = player_message['kda']
               money_count = player_message['money_count']
               money_minute = player_message['money_minute']
               offered_rate = player_message['offered_rate']
               score = player_message['score']
               equip_ids = player_message['equip_ids']
               skill_ids = player_message['skill_ids']
               position = player_message['player_position']
               position = position_list[position]
            # parse_import(matchTime)
#
# # 导入到数据库
# def  parse_import(matchTime):










# url_detail = 'https://www.shangniu.cn/api/battle/lol/match/liveBattle?battleId=26806339601'
# url_details = {1:url_detail}
# parse_detail(url_details, headers_yxlmgw, team_a_name, team_b_name)



for url in urls:
    parse(url_matchlist_l, headers_yxlmgw)