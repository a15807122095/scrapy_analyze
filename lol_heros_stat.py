# -*-coding:utf-8-*-

import requests
import json
from common_tool import post_response, league_check, team_check, api_return_200
from import_data_to_redis import RedisCache_checkAPI
from import_data_to_mysql import con_db
from setting import db_setting
from datetime import datetime

"""
战队排行榜（英雄联盟）
抓取规则：
每个联赛都有一个tournament_id,以post请求：https://www.scoregg.com/services/api_url.php
form_data 中主要有两个变动参数：tournament_id(联赛id), page(页数)
"""

start_url = 'https://www.scoregg.com/services/api_url.php'

header = {
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36'
}

league_exclude = ['2020 季中杯', '2020 LCK夏季升降级赛', '2019KeSPA杯', '2019LOL全明星']

# 请求英雄联盟联赛id的form_data  url:https://www.scoregg.com/services/api_url.php
form_data_yxlm = {
    'api_path': '/services/match/web_tournament_group_list.php',
    'method': 'GET',
    'platform': 'web',
    'api_version': '9.9.9',
    'language_id': 1,
    'gameID': 1,
    'type': 'all',
    'page': 1,
    'limit': 18,
    'year':''
}

# 请求王者荣耀联赛id的form_data  url:https://www.scoregg.com/services/api_url.php
form_data_wzry = {
'api_path': '/services/match/web_tournament_group_list.php',
'method': 'GET',
'platform': 'web',
'api_version': '9.9.9',
'language_id': 1,
'gameID': 2,
'type': 'all',
'page': 1,
'limit': 18,
'year':''
}

# 请求战队排行的form_data  url:https://www.scoregg.com/services/api_url.php
form_data = {
    'api_path': '/services/gamingDatabase/match_data_ssdb_list.php',
    'method': 'post',
    'platform': 'web',
    'api_version': '9.9.9',
    'language_id': 1,
    'tournament_id': 0,
    'type': 'team',
    'order_type': 'KDA',
    'order_value': 'DESC',
    'team_name': '',
    'player_name': '',
    'positionID': '',
    'page': 1
}



redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse(types):
    # game_name = '英雄联盟' if types ==1 else '王者荣耀'
    form_data_tournament = form_data_yxlm if types ==1 else form_data_wzry
    responses = post_response(start_url, form_data_tournament, header)
    responses = responses['data']['list']
    print('源数据：', responses)
    for response in responses:
        # 拿到联赛id
        tournamentID = response['tournamentID']
        source_league_name = response['name']
        # 过滤掉排除的联赛
        if source_league_name in league_exclude:
            continue

    # 访问后端拿到正确的联赛名
        result_league = league_check(source_league_name, types)
        print('访问后端得到的联赛结果：', result_league)
        league_name = result_league['result']['league_name']
        league_id = result_league['result']['league_id']

        if result_league['code'] == 600:
            # 战队榜单的url请求抓取2页,抓2次
            form_data['tournament_id'] = tournamentID
            for i in range(2):
                form_data['page'] = i+1
                responses = post_response(start_url, form_data, header)
                responses = responses['data']['data']['list']

                for responses_team in responses:
                    print('拿到的源数据：', responses_team)
                    team_name = responses_team['team_name']
                    # 访问后端拿到正确的团队名
                    result_team = team_check(team_name, types)
                    team_name = result_team['result']['team_name']
                    print('访问后端得到的团队结果：', result_team)

                    if result_team['code']:
                        team_id = result_team['result']['team_id']
                        win_count = responses_team['win']
                        lost_count = responses_team['los']
                        play_count = responses_team['MACTH_TIMES']
                        time_average = responses_team['AVERAGE_TIME']
                        # 存在比赛时长的,将时间转换为时间戳
                        if time_average:
                            time_average = time_average.split(':')
                            time_averages = int(time_average[0]) * 3600 + int(time_average[1]) * 60 + int(time_average[2])
                        else:
                            time_averages = 0
                        first_blood_rate = responses_team['FIRSTBLOODKILL']
                        small_dragon_rate = responses_team['SMALLDRAGON_RATE']
                        small_dragon_average = responses_team['AVERAGE_SMALLDRAGON']
                        big_dragon_rate = responses_team['BIGDRAGON_RATE']
                        big_dragon_average = responses_team['AVERAGE_BIGDRAGON']
                        tower_success_average = responses_team['AVERAGE_TOWER_SUCCESS']
                        tower_fail_average = responses_team['AVERAGE_TOWER_FAIL']
                        kda = responses_team['KDA']
                        kill_average = responses_team['AVERAGE_KILLS']
                        death_average = responses_team['AVERAGE_DEATHS']
                        assist_average = responses_team['AVERAGE_ASSISTS']
                        economic_average = responses_team['AVERAGE_MONEY']
                        economic_minute = responses_team['MINUTE_MONEY']
                        hit_minute = responses_team['MINUTE_HITS']
                        wards_placed_minute = responses_team['MINUTE_WARDSPLACED']
                        wards_killed_minute = responses_team['MINUTE_WARDSKILLED']
                        damage_average = responses_team['AVERAGE_CHAMPIONS']
                        damage_minute = responses_team['MINUTE_OUTPUT']
                        score = responses_team['f_score']
                        win_rate = responses_team['VICTORY_RATE']
                        # 一塔率网站上没有，先写0
                        first_tower_rate = 0

                        # 记录英雄联盟表

                        table = 'game_lol_team_league_stats' if types == 1 else 'game_kog_team_league_stats'
                        sql_teamrank_yxlm = "INSERT INTO `game_lol_team_league_stats` (team_id, league_id, play_count, win_rate," \
                                    " time_average, death_average, kill_average, economic_minute, first_blood_rate, tower_fail_average," \
                                    " tower_success_average, kda, damage_average, big_dragon_rate, big_dragon_average, small_dragon_rate," \
                                    "small_dragon_average, first_tower_rate, damage_minute, hit_minute, economic_average, type, " \
                                    "wards_placed_minute, wards_killed_minute) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, " \
                                    "{8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23}) " \
                                            "ON DUPLICATE KEY UPDATE " \
                                    "team_id={0}, league_id={1}, play_count={2}, win_rate={3}, time_average={4}, death_average={5}, " \
                                    "kill_average={6}, economic_minute={7}, first_blood_rate={8}, tower_fail_average={9}, " \
                                    "tower_success_average={10}, kda={11}, damage_average={12}, big_dragon_rate={13}, big_dragon_average={14}, " \
                                    "small_dragon_rate={15}, small_dragon_average={16}, first_tower_rate={17}, damage_minute={18}, " \
                                    "hit_minute={19}, economic_average={20}, type={21}, wards_placed_minute={22}, wards_killed_minute={23};".format(
                                    team_id, league_id, play_count, win_rate, time_averages, death_average, kill_average,
                                    economic_minute, first_blood_rate, tower_fail_average, tower_success_average, kda, damage_average,
                                    big_dragon_rate, big_dragon_average, small_dragon_rate, small_dragon_average, first_tower_rate,
                                    damage_minute, hit_minute, economic_average, types, wards_placed_minute, wards_killed_minute)





                        sql_teamrank_wzry = "INSERT INTO `game_kog_team_league_stats` (team_id, league_id, win_count, lost_count, " \
                                   "play_count, time_average, first_blood_rate, small_dragon_rate, small_dragon_average, " \
                                   "big_dragon_rate, big_dragon_average, tower_success_average, tower_fail_average, kda, " \
                                   "kill_average, death_average, assist_average, economic_average, economic_minute, hit_minute, " \
                                   "wards_placed_minute, wards_killed_minute, damage_average, damage_minute, score, win_rate" \
                                   ")  VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}," \
                                   "{16}, {17}, {18}, {19}, {20}, {21}, {22}, {23}, {24}, {25})" \
                                        "ON DUPLICATE KEY UPDATE "\
                                   "team_id={0}, league_id={1}, win_count={2}, lost_count={3}, play_count={4}, time_average={5}, " \
                                   "first_blood_rate={6}, small_dragon_rate={7}, small_dragon_average={8}, big_dragon_rate={9}, big_dragon_average={10}, " \
                                   "tower_success_average={11}, tower_fail_average={12}, kda={13}, kill_average={14}, " \
                                   "death_average={15}, assist_average={16}, economic_average={17}, economic_minute={18}," \
                                   "hit_minute={19}, wards_placed_minute={20}, wards_killed_minute={21}, damage_average={22}," \
                                   " damage_minute={23}, win_rate={24}, score={25};".format(team_id, league_id, win_count, lost_count,
                                   play_count, time_averages, first_blood_rate, small_dragon_rate, small_dragon_average,
                                   big_dragon_rate, big_dragon_average, tower_success_average, tower_fail_average, kda,
                                   kill_average, death_average, assist_average, economic_average, economic_minute, hit_minute,
                                   wards_placed_minute, wards_killed_minute, damage_average, damage_minute, win_rate, score, table)
                        sql_teamrank = sql_teamrank_yxlm if types == 1 else sql_teamrank_wzry
                        print('添加团队排行榜的类型以及sql:', types, sql_teamrank)
                        db.update_insert(sql_teamrank)

                    else:
                        # 记录到黑名单
                        sql_blacklist = "select id from api_check_200 where team_name = '{}';".format(team_name)
                        sql_add_blacklist = "insert into api_check_200 set team_name = '{}';".format(team_name)
                        print('记录到战队黑名单sql:', sql_add_blacklist)
                        api_return_200(sql_blacklist, sql_add_blacklist, db)



        else:
            # 记录到黑名单
            sql_blacklist = "select id from api_check_200 where league_name = '{}';".format(league_name)
            sql_add_blacklist = "insert into api_check_200 set league_name = '{}';".format(league_name)
            print('记录到联赛黑名单sql:', sql_add_blacklist)
            api_return_200(sql_blacklist, sql_add_blacklist, db)








# parse(1)
# print('英雄联盟抓取完成')
parse(2)
print('王者荣耀抓取完成')

