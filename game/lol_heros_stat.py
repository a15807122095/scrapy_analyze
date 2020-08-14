# -*-coding:utf-8-*-

from common_tool import post_response, league_check, api_return_200, hero_check, get_log
from db.import_data_to_redis import RedisCache_checkAPI
from db.import_data_to_mysql import con_db
from setting import db_setting

"""
英雄排行榜（英雄联盟,王者荣耀）
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

lol_heros_log = get_log('lol_heros')

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

# 请求英雄排行的form_data  url:https://www.scoregg.com/services/api_url.php
form_data = {
    'api_path': '/services/gamingDatabase/match_data_ssdb_list.php',
    'method': 'post',
    'platform': 'web',
    'api_version': '9.9.9',
    'language_id': 1,
    'tournament_id': 0,
    'type': 'hero',
    'order_type': 'APPEAR',
    'order_value': 'DESC',
    'team_name': '',
    'player_name': '',
    'positionID': '',
    'page': 1
}



redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse(types):
    try:
        # game_name = '英雄联盟' if types ==1 else '王者荣耀'
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
                for i in range(5):
                    form_data['page'] = i+1
                    responses = post_response(start_url, form_data, header)
                    if not responses:
                        continue
                    responses = responses['data']['data']['list']

                    for responses_hero in responses:
                        # print('拿到的源数据：', responses_hero)
                        hero_avatar = responses_hero['hero_image']
                        hero_name = responses_hero['hero_name']
                        # 根据英雄名称访问后端拿到正确的hero_id
                        result_hero = hero_check(hero_name, types)
                        # 只处理后端返回600的数据
                        if result_hero['code'] == 600:
                            hero_id = result_hero['result']['hero_id']
                            assist_average = responses_hero['AVERAGE_ASSISTS']
                            death_average = responses_hero['AVERAGE_DEATHS']
                            kill_average = responses_hero['AVERAGE_KILLS']
                            kda_average = responses_hero['KDA']
                            pick_rate = responses_hero['APPEAR']
                            ban_rate = responses_hero['PROHIBIT']
                            win_rate = responses_hero['VICTORY_RATE']
                            pick_count = responses_hero['appear_count']
                            ban_count = responses_hero['prohibit_count']
                            win_count = responses_hero['victory_count']
                            position = responses_hero['position_name']
                            # 记录英雄联盟表
                            sql_herorank_yxlm = "INSERT INTO `game_lol_heroes_league_stats` (hero_id, hero_avatar, hero_name, " \
                                        "assist_average, death_average, kill_average, kda_average, pick_rate, ban_rate, " \
                                        "win_rate, pick_count, ban_count, win_count, position, league_id) VALUES({0}, '{1}', " \
                                        "'{2}', {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, '{13}', {14}) " \
                                                "ON DUPLICATE KEY UPDATE " \
                                        "hero_id={0}, hero_avatar='{1}', hero_name='{2}', assist_average={3},death_average={4}," \
                                        " kill_average={5}, kda_average={6}, pick_rate={7}, ban_rate={8}, win_rate={9}, pick_count={10}," \
                                        "ban_count={11}, win_count={12}, position='{13}', league_id={14};".format(hero_id, hero_avatar, hero_name,
                                        assist_average, death_average, kill_average, kda_average, pick_rate, ban_rate,
                                        win_rate, pick_count, ban_count, win_count, position, league_id)

                            sql_herorank_wzry = "INSERT INTO `game_kog_heroes_league_stats` (hero_id, hero_avatar, hero_name, " \
                                        "assist_average, death_average, kill_average, kda_average, show_rate, ban_rate, " \
                                        "win_rate, pick_count, ban_count, win_count, league_id, position) VALUES({0}, " \
                                        "'{1}', '{2}', {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, '{14}') " \
                                        "ON DUPLICATE KEY UPDATE " \
                                        "hero_id={0}, hero_avatar='{1}', hero_name='{2}', assist_average={3},death_average={4}," \
                                        " kill_average={5}, kda_average={6}, show_rate={7}, ban_rate={8}, win_rate={9}, pick_count={10}," \
                                        "ban_count={11}, win_count={12}, league_id={13}, position='{14}';".format(hero_id, hero_avatar,
                                        hero_name, assist_average, death_average, kill_average, kda_average, pick_rate,
                                        ban_rate, win_rate, pick_count, ban_count, win_count, league_id, position)
                            sql_herorank = sql_herorank_yxlm if types == 1 else sql_herorank_wzry
                            # print('添加英雄排行榜的类型以及sql:', types, sql_herorank)
                            db.update_insert(sql_herorank)
                        else:
                            # 记录到黑名单中的英雄名称
                            sql_blacklist = "select id from black_list where hero_name = '{}';".format(hero_name)
                            sql_add_blacklist = "insert into black_list set league_name = '{0}',hero_name = '{1}', " \
                                                "source_from = 1, judge_position=0001;".format(league_name, hero_name)
                            # print('记录到英雄黑名单sql:', sql_add_blacklist)
                            api_return_200(sql_blacklist, sql_add_blacklist, db)

            else:
                # 记录到黑名单
                sql_blacklist = "select id from black_list where league_name = '{}';".format(league_name)
                sql_add_blacklist = "insert into black_list set league_name = '{}', source_from = 1, " \
                                    "judge_position=1000;".format(league_name)
                # print('记录到联赛黑名单sql:', sql_add_blacklist)
                api_return_200(sql_blacklist, sql_add_blacklist, db)
    except Exception as e:
        lol_heros_log.error(e, exc_info=True)









parse(1)
# print('英雄联盟抓取完成')
parse(2)
# print('王者荣耀抓取完成')

