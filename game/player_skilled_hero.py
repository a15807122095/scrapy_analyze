# -*-coding:utf-8-*-

import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')

from common_tool import post_response, league_check, api_return_200, player_check, hero_check

from import_data_to_redis import RedisCache_urldistict
from import_data_to_mysql import con_db
from setting import db_setting

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

league_exclude = ['2020 LCK夏季升降级赛', '2019KeSPA杯', '2019拉斯维加斯全明星', 'LPL公开训练赛', '2017 KPL秋季赛']
position_dict = {'上单':1, '打野':2, '中单':3, 'ADC':4, '辅助':5}
# player_skilled_hero_log = get_log('player_skilled_hero')

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

# 请求选手排行的form_data  url:https://www.scoregg.com/services/api_url.php
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

# 选手常用英雄的form_data  url:https://www.scoregg.com/services/api_url.php
form_data_hotheroes = {
    'api_path': '/services/gamingDatabase/player.php',
    'method': 'post',
    'platform': 'web',
    'api_version': '9.9.9',
    'language_id': '1',
    'playerID': '0',
    'teamID': '',
    # 'year': '2019',
    'tournamentID':'',
    'heroID': ''
}

redis = RedisCache_urldistict()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse(types):
    # try:
    source = 'score'
    form_data_tournament = form_data_yxlm if types ==1 else form_data_wzry
    responses = post_response(start_url, form_data_tournament, header)
    responses = responses['data']['list']
    # print('源数据：', responses)
    for response in responses:
        # 拿到联赛id
        tournamentID = response['tournamentID']
        source_league_name = response['name']
        # 过滤掉排除的联赛
        if source_league_name in league_exclude:
            continue

    # 访问后端拿到正确的联赛名
        result_league = league_check(source_league_name, types)
        # print('访问后端得到的联赛结果：', result_league)
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
                    # print('拿到的源数据：', responses_team)
                    player_name = responses_team['player_name']
                    source_player_id = responses_team['player_id']
                    # form_data_hotheroes中playerID为字符串类型，'year'可以不带
                    form_data_hotheroes['playerID'] = '{}'.format(source_player_id)
                    response_detail = post_response(start_url, form_data_hotheroes, header)
                    response_hot_heroes = response_detail['data']['data']['hot_heroes']

                    # 先从redis中找到player_id，有记录代表之前已记录，过滤掉
                    # redis存储结构：（源+player+source_player_id:player_id）‘score+player+8377:'123'
                    key_player = source + '+' + 'player' + '+' + source_player_id
                    result = redis.get_data(key_player)
                    # print('redis查询player的结果：', result)
                    if result:
                        player_id = result
                        parse_detail(response_hot_heroes, league_name, source, types, player_id)
                    else:
                        # redis中不存在就访问后端接口
                        result_player = player_check(player_name, types)
                        # print('访问后端拿到的选手信息：', result_player)
                        if result_player['code'] == 600:
                            player_id = result_player['result']['player_id']
                            # 记录到redis中，格式为：（源+player+source_player_id:player_id）‘score+player+8377:'123'
                            redis.set_data(key_player, 86400, player_id)
                            # print('redis记录player完成：',key_player, player_id)

                            parse_detail(response_hot_heroes, league_name, source, types, player_id)
                        else:
                            # 记录到黑名单中的选手名称
                            sql_blacklist = "select id from black_list where player_name ='{}';".format(player_name)
                            sql_add_blacklist = "insert into black_list set league_name = '{0}',player_name ='{1}', " \
                                                "source_from = 1, judge_position=0010;".format(league_name, player_name)
                            # print('记录到选手黑名单sql:', sql_add_blacklist)
                            api_return_200(sql_blacklist, sql_add_blacklist, db)
                            continue

        else:
            # 记录联赛到黑名单
            sql_blacklist = "select id from black_list where league_name = '{}';".format(league_name)
            sql_add_blacklist = "insert into black_list set league_name = '{}', source_from = 1, " \
                                "judge_position=1000;".format(league_name)
            # print('记录到联赛黑名单sql:', sql_add_blacklist)
            api_return_200(sql_blacklist, sql_add_blacklist, db)
    # except Exception as e:
    #     player_skilled_hero_log.error('联赛id关联选手异常')
    #     player_skilled_hero_log.error(e, exc_info=True)


def parse_detail(response_hot_heroes, league_name, source, types, player_id):
    # try:
    # 先删掉旧的数据
    parse_delete(player_id)
    for response_hot_hero in response_hot_heroes:
        source_hero_id = response_hot_hero['heroID']
        # 先从redis中找到hero_id，有记录代表之前已记录，直接取hero_id
        # redis存储结构：（源+player+source_hero_id:hero_id）‘score+hero+8377:'123'
        key_hero = source + '+' + 'hero' + '+' + source_hero_id
        result = redis.get_data(key_hero)
        # print('redis查询hero的结果：', result)
        if result:
            hero_id = result
            parse_insert(response_hot_hero, types, hero_id, player_id)
        else:
            hero_name = response_hot_hero['name']
            result_hero = hero_check(hero_name, types)
            if result_hero['code'] == 600:
                hero_id = result_hero['result']['hero_id']
                # 记录到redis中，格式为：（源+player+source_hero_id:hero_id）‘score+hero+8377:'123'
                redis.set_data(key_hero, 86400, hero_id)
                # print('redis记录player完成：', key_hero, hero_id)
                parse_insert(response_hot_hero, types, hero_id, player_id)
            else:
                # 记录到黑名单中的英雄名称
                sql_blacklist = "select id from black_list where hero_name='{}';".format(hero_name)
                sql_add_blacklist = "insert into black_list set league_name = '{0}',hero_name = '{1}', source_from = 1, " \
                                    "judge_position=0001;".format(league_name, hero_name)
                # print('记录到英雄黑名单sql:', sql_add_blacklist)
                api_return_200(sql_blacklist, sql_add_blacklist, db)
                continue
    # except Exception as e:
    #     player_skilled_hero_log.error('选手关联英雄异常')
    #     player_skilled_hero_log.error(e, exc_info=True)


def parse_delete(player_id):
    # try:
    # 拿到后端返回的player_id和hero_id开始记录
    # 1.找到对应选手的旧数据删掉，插入新数据（未找到选手直接插入）
    sql_checkplayer = 'select id from game_player_hero_stats where player_id = {}'.format(
        player_id)
    id_checkplayer = db.select_query(sql_checkplayer)
    # 找到之前的数据
    if len(id_checkplayer) > 1:
        sql_delete = 'delete from game_player_hero_stats where id in {};'.format(
            id_checkplayer)
        # print('删除一组旧数据sql:', sql_delete)
        db.update_insert(sql_delete)
    elif len(id_checkplayer) == 1:
        sql_delete = 'delete from game_player_hero_stats where id = {};'.format(
            id_checkplayer[0])
        # print('删除单个旧数据sql:', sql_delete)
        db.update_insert(sql_delete)
    # except Exception as e:
    #     player_skilled_hero_log.error('删除旧数据异常')
    #     player_skilled_hero_log.error(e, exc_info=True)


def parse_insert(response_hot_hero,types, hero_id, player_id):
    # try:
    kda = response_hot_hero['kda']
    kill_average = response_hot_hero['kills']
    death_average = response_hot_hero['deaths']
    assist_average = response_hot_hero['assists']
    score = response_hot_hero['score']
    win_count = response_hot_hero['wins']
    play_count = response_hot_hero['wins']
    win_rate = response_hot_hero['victory_rate']
    hero_avatar = response_hot_hero['image']

    # 2.插入新的数据
    sql_insert = "INSERT INTO `game_player_hero_stats` (hero_id, player_id, kda, kill_average, death_average, " \
                 "assist_average, score, win_count, play_count, win_rate, type, hero_avatar) VALUES({0}, {1}, {2}, {3}, " \
                 "{4}, {5}, {6}, {7}, {8}, {9}, {10}, '{11}');".format(hero_id, player_id, kda, kill_average, death_average,
                 assist_average, score, win_count, play_count, win_rate, types, hero_avatar)
    # print('更新选手擅长英雄表：', sql_insert)
    db.update_insert(sql_insert)
    # print('更新完成')
    # except Exception as e:
    #     player_skilled_hero_log.error('更新数据库异常')
    #     player_skilled_hero_log.error(e, exc_info=True)

parse(1)
# print('英雄联盟抓取完成')
parse(2)
# print('王者荣耀抓取完成')

