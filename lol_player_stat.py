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
position_dict = {'上单':1, '打野':2, '中单':3, 'ADC':4, '辅助':5}

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
    'type': 'player',
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
                    result_player = team_check(team_name, types)
                    team_name = result_player['result']['team_name']
                    team_id = result_player['result']['team_id']

                    print('访问后端得到的团队结果：', result_player)

                    if result_player['code']==600:
                        # player_id存的网站的，不知道对不对
                        player_id = responses_team['player_id']
                        kda = responses_team['KDA']
                        mvp_count = responses_team['MVP']
                        play_count = responses_team['PLAYS_TIMES']
                        win_count = responses_team['win']
                        lose_count = responses_team['los']
                        offered_rate = responses_team['OFFERED_RATE']
                        kill_count = responses_team['total_kills']
                        kill_average = responses_team['AVERAGE_KILLS']
                        assist_count = responses_team['total_assists']
                        assist_average = responses_team['AVERAGE_ASSISTS']
                        death_count = responses_team['total_deaths']
                        death_average = responses_team['AVERAGE_DEATHS']
                        economic_minute = responses_team['MINUTE_ECONOMIC']
                        hit_minute = responses_team['MINUTE_HITS']
                        damage_deal_minute = responses_team['MINUTE_DAMAGEDEALT']
                        damage_deal_rate = responses_team['DAMAGEDEALT_RATE']
                        damage_taken_minute = responses_team['MINUTE_DAMAGETAKEN']
                        damage_taken_rate = responses_team['DAMAGETAKEN_RATE']
                        wards_killed_minute = responses_team['MINUTE_WARDKILLED']
                        wards_placed_minute = responses_team['MINUTE_WARDSPLACED']

                        # 场均不到网站上没有，先写0
                        last_hit_per_game = 0
                        # 不确定网站上的total_kill, total_deaths, total_assists
                        # 到底是总的（击杀数）还是最高的（击杀数）
                        most_kill_per_games = responses_team['total_kills']
                        most_death_per_games = responses_team['total_deaths']
                        most_assist_per_games = responses_team['total_assists']
                        nick_name = responses_team['player_name']
                        avatar = responses_team['player_image']
                        position = responses_team['position']
                        position = position_dict[position]

                        # 记录英雄联盟表

                        sql_teamrank_yxlm = "INSERT INTO `game_lol_player_league_stats` (player_id, league_id, kda, " \
                                    "mvp_count, play_count, win_count, offered_rate, kill_count, kill_average, assist_count," \
                                    " assist_average, death_count, death_average, economic_minute, hit_minute, damage_deal_minute," \
                                    "damage_deal_rate, damage_taken_minute, damage_taken_rate, last_hit_per_game, " \
                                    "most_kill_per_games, most_death_per_games, most_assist_per_games, team_id, nick_name, avatar," \
                                    " position) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, " \
                                    "{12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23}, '{24}', '{25}', {26}) " \
                                            "ON DUPLICATE KEY UPDATE " \
                                    "player_id={0}, league_id={1}, kda={2}, mvp_count={3}, play_count={4}, win_count={5}, " \
                                    "offered_rate={6}, kill_count={7}, kill_average={8}, assist_count={9}, assist_average={10}, " \
                                    "death_count={11}, death_average={12}, economic_minute={13}, hit_minute={14}, " \
                                    "damage_deal_minute={15}, damage_deal_rate={16}, damage_taken_minute={17}, " \
                                    "damage_taken_rate={18}, last_hit_per_game={19}, most_kill_per_games={20}, " \
                                    "most_death_per_games={21}, most_assist_per_games={22}, team_id={23}, nick_name='{24}', avatar='{25}', " \
                                    "position={26};".format(player_id, league_id, kda, mvp_count, play_count, win_count,
                                    offered_rate, kill_count, kill_average, assist_count, assist_average, death_count,
                                    death_average, economic_minute, hit_minute, damage_deal_minute, damage_deal_rate,
                                    damage_taken_minute, damage_taken_rate, last_hit_per_game, most_kill_per_games,
                                    most_death_per_games, most_assist_per_games, team_id, nick_name, avatar, position)




                        sql_teamrank_wzry = "INSERT INTO `game_kog_player_league_stats` (player_id, league_id, win_count, " \
                                    "lose_count, play_count, mvp_count, kda, kill_count, kill_average, assist_count," \
                                    " assist_average, death_count, death_average, offered_rate, economic_minute, hit_minute," \
                                    "wards_placed_minute, wards_killed_minute, damage_deal_rate, damage_deal_minute, damage_taken_minute, " \
                                    "damage_taken_rate,  type, team_id, nick_name, avatar, position) VALUES({0}, " \
                                    "{1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}," \
                                    " {17}, {18}, {19}, {20},  {21}, {22}, {23}, '{24}', '{25}', {26}) " \
                                            "ON DUPLICATE KEY UPDATE " \
                                    "player_id={0}, league_id={1}, win_count={2}, lose_count={3}, play_count={4}, mvp_count={5}, " \
                                    "kda={6}, kill_count={7}, kill_average={8}, assist_count={9}, assist_average={10}, " \
                                    "death_count={11}, death_average={12}, offered_rate={13}, economic_minute={14}, " \
                                    "hit_minute={15}, wards_placed_minute={16}, wards_killed_minute={17}, " \
                                    "damage_deal_rate={18}, damage_deal_minute={19}, damage_taken_minute={20}, " \
                                    "damage_taken_rate={21}, type={22}, team_id={23}, nick_name='{24}', avatar='{25}'," \
                                    "position={26};".format(player_id, league_id, win_count, lose_count, play_count,
                                    mvp_count, kda, kill_count, kill_average, assist_count, assist_average, death_count,
                                    death_average, offered_rate, economic_minute, hit_minute, wards_placed_minute, wards_killed_minute,
                                    damage_deal_rate, damage_deal_minute, damage_taken_minute, damage_taken_rate,
                                    types, team_id, nick_name, avatar, position)
                        sql_teamrank = sql_teamrank_yxlm if types == 1 else sql_teamrank_wzry
                        print('添加选手排行榜的类型以及sql:', types, sql_teamrank)
                        db.update_insert(sql_teamrank)

                    else:
                        # 记录到黑名单
                        sql_blacklist = "select id from api_check_200 where team_name = '{}';".format(team_name)
                        sql_add_blacklist = "insert into api_check_200 set team_name = '{}';".format(team_name)
                        print('记录到选手黑名单sql:', sql_add_blacklist)
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

