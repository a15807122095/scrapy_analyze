# -*-coding:utf-8-*-
import json
import requests
from common_tool import post_response, get_log, get_weeks, get_response, redis_check, \
    player_check, api_return_200, hero_check
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_checkAPI
from datetime import datetime, timedelta
from setting import db_setting
import json


"""
英雄联盟赛事详情爬虫
从score网站上抓取 # start_url：https://www.scoregg.com/schedule
抓取流程：
从start_url中拿到昨天和今天的网站的赛事,通过过滤赛程类型来选择要抓取的赛事详情,其中的result就是该赛事打了几局,拿到里面的resultID
用resultID拼凑出对局详情的数据 :'https://img1.famulei.com/match/result/21952.json?_=1596076077396'
再根据接口返回数据分析入库
"""

match_detail_score_log = get_log('match_detail_score')

# 现有需要的联赛
tournamentID = {
    '170': '2020 LCS夏季赛',
    '171': '2020 LEC夏季赛',
    '172': '2020 LPL夏季赛',
    '173': '2020 LCK夏季赛',
    '174': '2020 LDL夏季赛'
}

# 对应位置的字典
position_dict = {
    'blue_hero_a_name':1, 'blue_hero_b_name':2, 'blue_hero_c_name':3, 'blue_hero_d_name':4, 'blue_hero_e_name':5,
    'red_hero_a_name':1, 'red_hero_b_name':2, 'red_hero_c_name':3, 'red_hero_d_name':4, 'red_hero_e_name':5
}

# 英雄等级字典
level_dict = {
    'blue_hero_a_name':'blue_hero_a_lv', 'blue_hero_b_name':'blue_hero_b_lv', 'blue_hero_c_name':'blue_hero_c_lv',
    'blue_hero_d_name':'blue_hero_d_lv', 'blue_hero_e_name':'blue_hero_e_lv', 'red_hero_a_name':'red_hero_a_lv',
    'red_hero_b_name':'red_hero_b_lv', 'red_hero_c_name':'red_hero_c_lv', 'red_hero_d_name':'red_hero_d_lv',
    'red_hero_e_name':'red_hero_e_lv'
}

# 英雄头像字典
avatar_dict = {
    'blue_hero_a_name':'blue_hero_a_pic', 'blue_hero_b_name':'blue_hero_b_pic', 'blue_hero_c_name':'blue_hero_c_pic',
    'blue_hero_d_name':'blue_hero_d_pic', 'blue_hero_e_name':'blue_hero_e_pic', 'red_hero_a_name':'red_hero_a_pic',
    'red_hero_b_name':'red_hero_b_pic', 'red_hero_c_name':'red_hero_c_pic', 'red_hero_d_name':'red_hero_d_pic',
    'red_hero_e_name':'red_hero_e_pic'
}

# 选手补刀字典
last_hit_dict = {
    'blue_hero_a_name':'blue_star_a_hits', 'blue_hero_b_name':'blue_star_b_hits', 'blue_hero_c_name':'blue_star_c_hits',
    'blue_hero_d_name':'blue_star_d_hits', 'blue_hero_e_name':'blue_star_e_hits', 'red_hero_a_name':'red_star_a_hits',
    'red_hero_b_name':'red_star_b_hits', 'red_hero_c_name':'red_star_c_hits', 'red_hero_d_name':'red_star_d_hits',
    'red_hero_e_name':'red_star_e_hits'
}

# 选手伤害字典
last_damage_dict = {
    'blue_hero_a_name':'blue_star_a_atk_o', 'blue_hero_b_name':'blue_star_b_atk_o', 'blue_hero_c_name':'blue_star_c_atk_o',
    'blue_hero_d_name':'blue_star_d_atk_o', 'blue_hero_e_name':'blue_star_e_atk_o', 'red_hero_a_name':'red_star_a_atk_o',
    'red_hero_b_name':'red_star_b_atk_o', 'red_hero_c_name':'red_star_c_atk_o', 'red_hero_d_name':'red_star_d_atk_o',
    'red_hero_e_name':'red_star_e_atk_o'
}

# 选手每分钟伤害字典
last_per_damage_dict = {
    'blue_hero_a_name':'blue_star_a_atk_m', 'blue_hero_b_name':'blue_star_b_atk_m', 'blue_hero_c_name':'blue_star_c_atk_m',
    'blue_hero_d_name':'blue_star_d_atk_m', 'blue_hero_e_name':'blue_star_e_atk_m', 'red_hero_a_name':'red_star_a_atk_m',
    'red_hero_b_name':'red_star_b_atk_m', 'red_hero_c_name':'red_star_c_atk_m', 'red_hero_d_name':'red_star_d_atk_m',
    'red_hero_e_name':'red_star_e_atk_m'
}

# 选手伤害占比字典
last_damage_rate_dict = {
    'blue_hero_a_name':'blue_star_a_atk_p', 'blue_hero_b_name':'blue_star_b_atk_p', 'blue_hero_c_name':'blue_star_c_atk_p',
    'blue_hero_d_name':'blue_star_d_atk_p', 'blue_hero_e_name':'blue_star_e_atk_p', 'red_hero_a_name':'red_star_a_atk_p',
    'red_hero_b_name':'red_star_b_atk_p', 'red_hero_c_name':'red_star_c_atk_p', 'red_hero_d_name':'red_star_d_atk_p',
    'red_hero_e_name':'red_star_e_atk_p'
}

# 选手承受伤害字典
last_damage_taken_dict = {
    'blue_hero_a_name':'blue_star_a_def_o', 'blue_hero_b_name':'blue_star_b_def_o', 'blue_hero_c_name':'blue_star_c_def_o',
    'blue_hero_d_name':'blue_star_d_def_o', 'blue_hero_e_name':'blue_star_e_def_o', 'red_hero_a_name':'red_star_a_def_o',
    'red_hero_b_name':'red_star_b_def_o', 'red_hero_c_name':'red_star_c_def_o', 'red_hero_d_name':'red_star_d_def_o',
    'red_hero_e_name':'red_star_e_def_o'
}

# 选手每分钟承受伤害字典
last_per_damage_taken_dict = {
    'blue_hero_a_name':'blue_star_a_def_m', 'blue_hero_b_name':'blue_star_b_def_m', 'blue_hero_c_name':'blue_star_c_def_m',
    'blue_hero_d_name':'blue_star_d_def_m', 'blue_hero_e_name':'blue_star_e_def_m', 'red_hero_a_name':'red_star_a_def_m',
    'red_hero_b_name':'red_star_b_def_m', 'red_hero_c_name':'red_star_c_def_m', 'red_hero_d_name':'red_star_d_def_m',
    'red_hero_e_name':'red_star_e_def_m'
}

# 选手承受伤害占比字典
last_damage_taken_rate_dict = {
    'blue_hero_a_name':'blue_star_a_def_p', 'blue_hero_b_name':'blue_star_b_def_p', 'blue_hero_c_name':'blue_star_c_def_p',
    'blue_hero_d_name':'blue_star_d_def_p', 'blue_hero_e_name':'blue_star_e_def_p', 'red_hero_a_name':'red_star_a_def_p',
    'red_hero_b_name':'red_star_b_def_p', 'red_hero_c_name':'red_star_c_def_p', 'red_hero_d_name':'red_star_d_def_p',
    'red_hero_e_name':'red_star_e_def_p'
}

# 选手kda字典
kda_dict = {
    'blue_hero_a_name':'blue_star_a_kda', 'blue_hero_b_name':'blue_star_b_kda', 'blue_hero_c_name':'blue_star_c_kda',
    'blue_hero_d_name':'blue_star_d_kda', 'blue_hero_e_name':'blue_star_e_kda', 'red_hero_a_name':'red_star_a_kda',
    'red_hero_b_name':'red_star_b_kda', 'red_hero_c_name':'red_star_c_kda', 'red_hero_d_name':'red_star_d_kda',
    'red_hero_e_name':'red_star_e_kda'
}

# 选手经济字典
money_count_dict = {
    'blue_hero_a_name':'blue_star_a_money_o', 'blue_hero_b_name':'blue_star_b_money_o', 'blue_hero_c_name':'blue_star_c_money_o',
    'blue_hero_d_name':'blue_star_d_money_o', 'blue_hero_e_name':'blue_star_e_money_o', 'red_hero_a_name':'red_star_a_money_o',
    'red_hero_b_name':'red_star_b_money_o', 'red_hero_c_name':'red_star_c_money_o', 'red_hero_d_name':'red_star_d_money_o',
    'red_hero_e_name':'red_star_e_money_o'
}

# 选手每分钟经济字典
money_minute_dict = {
    'blue_hero_a_name':'blue_star_a_money_M', 'blue_hero_b_name':'blue_star_b_money_M', 'blue_hero_c_name':'blue_star_c_money_M',
    'blue_hero_d_name':'blue_star_d_money_M', 'blue_hero_e_name':'blue_star_e_money_M', 'red_hero_a_name':'red_star_a_money_M',
    'red_hero_b_name':'red_star_b_money_M', 'red_hero_c_name':'red_star_c_money_M', 'red_hero_d_name':'red_star_d_money_M',
    'red_hero_e_name':'red_star_e_money_M'
}

# 选手参团率字典
offered_rate_dict = {
    'blue_hero_a_name':'blue_star_a_part', 'blue_hero_b_name':'blue_star_b_part', 'blue_hero_c_name':'blue_star_c_part',
    'blue_hero_d_name':'blue_star_d_part', 'blue_hero_e_name':'blue_star_e_part', 'red_hero_a_name':'red_star_a_part',
    'red_hero_b_name':'red_star_b_part', 'red_hero_c_name':'red_star_c_part', 'red_hero_d_name':'red_star_d_part',
    'red_hero_e_name':'red_star_e_part'
}

# 选手得分字典
score_dict = {
    'blue_hero_a_name':'blue_star_a_score', 'blue_hero_b_name':'blue_star_b_score', 'blue_hero_c_name':'blue_star_c_score',
    'blue_hero_d_name':'blue_star_d_score', 'blue_hero_e_name':'blue_star_e_score', 'red_hero_a_name':'red_star_a_score',
    'red_hero_b_name':'red_star_b_score', 'red_hero_c_name':'red_star_c_score', 'red_hero_d_name':'red_star_d_score',
    'red_hero_e_name':'red_star_e_score'
}

# 需要常规遍历填充的字典,依次为：等级，头像，补刀，伤害，分均伤害，伤害占比，承受伤害，分均承伤，承伤占比，kda，经济，分均经济，参团率，得分
iter_list = [level_dict, avatar_dict, last_hit_dict, last_damage_dict, last_per_damage_dict, last_damage_rate_dict,
             last_damage_taken_dict, last_per_damage_taken_dict, last_damage_taken_rate_dict, kda_dict, money_count_dict,
             money_minute_dict, offered_rate_dict, score_dict]

# 选手装备字典
equip_ids_dict = {
    'blue_hero_a_name':['blue_star_a_equip_1', 'blue_star_a_equip_2', 'blue_star_a_equip_3', 'blue_star_a_equip_4',
                        'blue_star_a_equip_5', 'blue_star_a_equip_6', 'blue_star_a_equip_7'],
    'blue_hero_b_name':['blue_star_b_equip_1', 'blue_star_b_equip_2', 'blue_star_b_equip_3', 'blue_star_b_equip_4',
                        'blue_star_b_equip_5', 'blue_star_b_equip_6', 'blue_star_b_equip_7'],
    'blue_hero_c_name':['blue_star_c_equip_1', 'blue_star_c_equip_2', 'blue_star_c_equip_3', 'blue_star_c_equip_4',
                        'blue_star_c_equip_5', 'blue_star_c_equip_6', 'blue_star_c_equip_7'],
    'blue_hero_d_name':['blue_star_d_equip_1', 'blue_star_d_equip_2', 'blue_star_d_equip_3', 'blue_star_d_equip_4',
                        'blue_star_d_equip_5', 'blue_star_d_equip_6', 'blue_star_d_equip_7'],
    'blue_hero_e_name':['blue_star_e_equip_1', 'blue_star_e_equip_2', 'blue_star_e_equip_3', 'blue_star_e_equip_4',
                        'blue_star_e_equip_5', 'blue_star_e_equip_6', 'blue_star_e_equip_7'],
    'red_hero_a_name':['red_star_a_equip_1', 'red_star_a_equip_2', 'red_star_a_equip_3', 'red_star_a_equip_4',
                        'red_star_a_equip_5', 'red_star_a_equip_6', 'red_star_a_equip_7'],
    'red_hero_b_name':['red_star_b_equip_1', 'red_star_b_equip_2', 'red_star_b_equip_3', 'red_star_b_equip_4',
                        'red_star_b_equip_5', 'red_star_b_equip_6', 'red_star_b_equip_7'],
    'red_hero_c_name':['red_star_c_equip_1', 'red_star_c_equip_2', 'red_star_c_equip_3', 'red_star_c_equip_4',
                        'red_star_c_equip_5', 'red_star_c_equip_6', 'red_star_c_equip_7'],
    'red_hero_d_name':['red_star_d_equip_1', 'red_star_d_equip_2', 'red_star_d_equip_3', 'red_star_d_equip_4',
                        'red_star_d_equip_5', 'red_star_d_equip_6', 'red_star_d_equip_7'],
    'red_hero_e_name':['red_star_e_equip_1', 'red_star_e_equip_2', 'red_star_e_equip_3', 'red_star_e_equip_4',
                        'red_star_e_equip_5', 'red_star_e_equip_6', 'red_star_e_equip_7']
}

# 选手技能字典
skill_ids_dict = {
    'blue_hero_a_name':['blue_a_skill_1', 'blue_a_skill_2'],
    'blue_hero_b_name':['blue_b_skill_1', 'blue_b_skill_2'],
    'blue_hero_c_name':['blue_b_skill_1', 'blue_b_skill_2'],
    'blue_hero_d_name':['blue_b_skill_1', 'blue_b_skill_2'],
    'blue_hero_e_name':['blue_b_skill_1', 'blue_b_skill_2'],
    'red_hero_a_name':['red_a_skill_1', 'red_a_skill_2'],
    'red_hero_b_name':['red_b_skill_1', 'red_b_skill_2'],
    'red_hero_c_name':['red_c_skill_1', 'red_c_skill_2'],
    'red_hero_d_name':['red_d_skill_1', 'red_d_skill_2'],
    'red_hero_e_name':['red_e_skill_1', 'red_e_skill_2']
}

#得到上周的日期和这周到今天的日期字符串列表：
date_list = get_weeks()
# print(date_list)

# 拿到上周五的日期字符串
now_date = datetime.now()
now_date_stamp = str(int(now_date.timestamp()*1000))
last_friday = now_date - timedelta(days=(now_date.weekday()+1))
last_friday_str = last_friday.strftime('%Y-%m-%d')

start_url = 'https://www.scoregg.com/services/api_url.php'

detail_url = 'https://img1.famulei.com/match/result/{0}.json?_={1}'

headers = {
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/84.0.4147.89 Safari/537.36'
}

# 创建redis对象
redis = RedisCache_checkAPI()
# 创建mysql连接对象
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

form_data = {
'api_path': 'services/match/web_math_list.php',
'gameID': '1',
'date': '',
'tournament_id': '',
'api_version': '9.9.9',
'platform': 'web'
}

def parse(url, data, headers):
    types = 1
    game_name = '英雄联盟'
    source_from = 'score详情赛事' # 爬虫网站源
    # try:
    results = post_response(url, data, headers)
    results = results['data']['list']
    # print('需要拿的赛程日期:', date_list)
    # print(len(results), type(results), results)
    for key_list, results_list in results.items():
        # 排除掉今天和昨天之外的赛程
        if key_list not in date_list:
            continue
        result_list = results_list['info']
        # print('所有赛程:', key_list, type(result_list), result_list)
        for key_detail, results_detail in result_list.items():
            # 排除不需要的联赛
            if key_detail not in tournamentID:
                continue
            league_name = tournamentID[key_detail]
            # print('现有联赛：', key_detail, results_detail)
            results_detail = results_detail['list']
            for detail_list in results_detail:
                # 拿到网站的赛程id，用于后面redis_check
                source_matchid = detail_list['match_id']
                # 网站赛事的比赛时间为 "2020-07-30"和 "17:00" 转换为十位的时间戳
                start_time_str = detail_list['start_date'] + ' ' + detail_list['start_time'] + ':00'
                start_time_date = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                start_time = int(start_time_date.timestamp())
                detail_list = detail_list['result']
                # print('得到的时间：', start_time_str, start_time_date, detail_list)
                if detail_list:
                    # 以detail_list中遍历次数计为bo
                    index_num = 1
                    for resultID in detail_list:
                        # 赛程的小局id,用这个id存到对局详情表中才能作为判断更新或插入条件
                        resultID = resultID['resultID']
                        detail_urls = detail_url.format(resultID, now_date_stamp)
                        # print('详情url：', resultID, detail_urls)
                        detail_parse(detail_urls, source_matchid, resultID, types, index_num, game_name,
                                     league_name, start_time, headers)
                        index_num += 1
    # except Exception as e:
    #     match_detail_score_log.error(e)



def detail_parse(url, source_matchid, resultID, types, index_num, game_name, league_name, start_time, headers):
    result_all = get_response(url, headers)
    # print('详情数据：', result_all)
    source = 'score'
    last_hit_minute = 0

    if result_all:
        # 将选手信息与英雄信息以键值对的形式存到字典中 ,
        # 字典形式:{‘hero_name’：['player_name','player_id','hero_id'],......}
        # 例如：{ ‘荒漠屠夫’：['bin', 'player_id', 'player_avatar', 'hero_id'],......}
        team_result = result_all['data']['teams']
        hero_player_dict = {}
        for player_result in team_result:
            # 选手id需要跟后端匹配拿到正确的player_id
            player_name = player_result['nickname']
            # 先从redis中找到player_id，有记录代表之前已记录,取出player
            # redis存储结构：（源+player+player_name:player_id）‘score+player+uzi:'123'
            key_player = source + '+' + 'player' + '+' + player_name
            result = redis.get_data(key_player)
            # print('redis查询player的结果：', result)
            if result:
                # print('redis有记录：', result)
                player_id = result
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
                else:
                    # 记录到黑名单中的选手名称
                    sql_blacklist = "select id from black_list where player_name ='{}';".format(player_name)
                    sql_add_blacklist = "insert into black_list set league_name = '{0}',player_name ='{1}', " \
                                        "source_from = 1, judge_position=0010;".format(league_name, player_name)
                    # print('记录到选手黑名单sql:', sql_add_blacklist)
                    player_id = None
                    api_return_200(sql_blacklist, sql_add_blacklist, db)
            # 存在player_id
            if player_id:
                # 继续拿到选手其他数据
                player_avatar = player_result['player_image_thumb']
                hero_name = player_result['hero_name']
                kill_count = player_result['kills']
                death_count = player_result['deaths']
                assist_count = player_result['assists']
                team_color = player_result['color']

                # 先从redis中找到hero_id，有记录代表之前已记录，直接取hero_id
                # redis存储结构：（源+player+hero_name:hero_id）‘score+hero+8377:'123'
                key_hero = source + '+' + 'hero' + '+' + hero_name
                result = redis.get_data(key_hero)
                # print('redis查询hero的结果：', result)
                if result:
                    hero_id = result
                else:
                    result_hero = hero_check(hero_name, types)
                    if result_hero['code'] == 600:
                        hero_id = result_hero['result']['hero_id']
                        # 记录到redis中，格式为：（源+player+source_hero_id:hero_id）‘score+hero+8377:'123'
                        redis.set_data(key_hero, 86400, hero_id)
                        # print('redis记录hero完成：', key_hero, hero_id)
                    else:
                        # 记录到黑名单中的英雄名称
                        sql_blacklist = "select id from black_list where hero_name='{}';".format(hero_name)
                        sql_add_blacklist = "insert into black_list set league_name = '{0}',hero_name = '{1}', " \
                                            "source_from = 1, judge_position=0001;".format(league_name, hero_name)
                        # print('记录到英雄黑名单sql:', sql_add_blacklist)
                        api_return_200(sql_blacklist, sql_add_blacklist, db)
                        hero_id = None

                # 存在hero_id
                if hero_id:
                    hero_player_dict[hero_name] = [player_name, player_id, player_avatar, hero_id, kill_count,
                                                     assist_count, death_count, team_color]
        # print('英雄选手字典:', hero_player_dict)

        result = result_all['data']['result_list']
        # 先暂且把蓝方当主队，红方当客队请求后端拿到规范后的队名
        home_team = result['blue_name']
        guest_name = result['red_name']
        # redis中加入网站源标记
        result_check = redis_check(redis, game_name, db, source, league_name, source_matchid, home_team, guest_name, start_time)
        match_id = result_check[0]
        # match_id, league_id, team_a_id, tea_b_id, team_a_name, tea_b_name, league_name
        # 后端返回600且match_id不为空，说明对局详情在赛程表中匹配到赛程
        if result_check and match_id:
            # 网站的比赛时长有个‘game_time_m’代表分钟，‘game_time_s’代表秒
            duration = int(result['game_time_m'])*60 + int(result['game_time_s'])
            # print('比赛时长：', result['game_time_m'], result['game_time_s'], duration)
            status = 1
            team_a_name = result_check[4]
            team_b_name = result_check[5]
            sql_check = 'select team_a_name, team_a_id, team_b_name, team_b_id from game_python_match ' \
                        'where id = {}'.format(match_id)
            result_team = db.select_message(sql_check)
            team_a_realname = result_team[0]
            team_b_realname = result_team[2]
            team_a_id = result_team[1]
            team_b_id = result_team[3]
            judge_reversal = False
            # 正常情况下网站的a,b队就是表中的a，b队
            team_judge = {'blue':team_a_id, 'red':team_b_id}
            # 如果score网站的a（蓝），b（红）队校正后与表中a,b队相反，以表为准，此时score的b队是主队
            if team_a_name == team_b_realname and team_b_name == team_a_realname:
                judge_reversal = True
                team_judge = {'red': team_a_id, 'blue': team_b_id}
            # print('a,b队的名字：',judge_reversal, home_team, team_a_name, team_a_realname, team_a_id,
            #       guest_name, team_b_name, team_b_realname, team_b_id)

            # 团队的数据
            team_a_kill_count = result['red_kill'] if judge_reversal else result['blue_kill']
            team_b_kill_count = result['blue_kill'] if judge_reversal else result['red_kill']
            team_a_death_count = result['red_die'] if judge_reversal else result['blue_die']
            team_b_death_count = result['blue_die'] if judge_reversal else result['red_die']
            team_a_assist_count = result['red_asses'] if judge_reversal else result['blue_asses']
            team_b_assist_count = result['blue_asses'] if judge_reversal else result['red_asses']
            team_a_big_dragon_count = result['red_big_dargon'] if judge_reversal else result['blue_big_dargon']
            team_b_big_dragon_count = result['blue_big_dargon'] if judge_reversal else result['red_big_dargon']
            team_a_small_dragon_count = result['red_small_dargon'] if judge_reversal else result['blue_small_dargon']
            team_b_small_dragon_count = result['blue_small_dargon'] if judge_reversal else result['red_small_dargon']
            team_a_tower_count = result['red_tower'] if judge_reversal else result['blue_tower']
            team_b_tower_count = result['blue_tower'] if judge_reversal else result['red_tower']
            team_a_money = result['red_money'] if judge_reversal else result['blue_money']
            team_b_money = result['blue_money'] if judge_reversal else result['red_money']
            team_a_side = 'red' if judge_reversal else 'blue'
            team_b_side = 'blue' if judge_reversal else 'red'
            # win_teamID为A队id则A队赢，否则B队赢
            win_team = 'A' if result['win_teamID'] == result['teamID_a'] else 'B'
            dragon_result = result_all['data']['dragon_list']
            if not judge_reversal:
                first_big_dragon_team = 'A' if dragon_result['blue']['firstDragonKill'] else 'B'
                first_small_dragon_team = 'A' if dragon_result['blue']['firstBaronKill'] else 'B'
                first_blood_team = 'A' if dragon_result['blue']['firstBloodKill'] else 'B'
                first_tower_team = 'A' if dragon_result['blue']['firstTowerKill'] else 'B'
                team_a_five_kills = 1 if dragon_result['blue']['first5Kill'] else 0
                team_b_five_kills = 1 if dragon_result['red']['first5Kill'] else 0
                team_a_ten_kills = 1 if dragon_result['blue']['first10Kill'] else 0
                team_b_ten_kills = 1 if dragon_result['red']['first10Kill'] else 0
            else:
                first_big_dragon_team = 'B' if dragon_result['blue']['firstDragonKill'] else 'A'
                first_small_dragon_team = 'B' if dragon_result['blue']['firstBaronKill'] else 'A'
                first_blood_team = 'B' if dragon_result['blue']['firstBloodKill'] else 'A'
                first_tower_team = 'B' if dragon_result['blue']['firstTowerKill'] else 'A'
                team_a_five_kills = 1 if dragon_result['red']['first5Kill'] else 0
                team_b_five_kills = 1 if dragon_result['blue']['first5Kill'] else 0
                team_a_ten_kills = 1 if dragon_result['red']['first10Kill'] else 0
                team_b_ten_kills = 1 if dragon_result['blue']['first10Kill'] else 0

            #在常规遍历列表中，以相同方式将值补充到hero_player_dict的值列表
            # 等级，头像，补刀，伤害，分均伤害，伤害占比，承受伤害，分均承伤，
            # 承伤占比，kda，经济，分均经济，参团率，得分
            # 在列表中的索引为：8,9,10,11,12,13,14,15,16,17, 18,19,20,21
            for iter_obj in iter_list:
                for key, value in iter_obj.items():
                    hero_sourcename = result[key]
                    hero_player_dict[hero_sourcename].append(result[value])
            # print('添加8-21值索引后的英雄选手字典', hero_player_dict)


            # 选手的位置数据补充到hero_player_dict的值列表索引为22
            for key, value in position_dict.items():
                hero_sourcename = result[key]
                hero_player_dict[hero_sourcename].append(value)
            # print('添加22值索引后的英雄选手字典', hero_player_dict)

            # 选手的装备数据补充到hero_player_dict的值列表索引为23
            # 值存储为json格式,存储到equip_ids_list中

            for key, values in equip_ids_dict.items():
                equip_ids_list = []
                hero_sourcename = result[key]
                for value in values:
                    value = result[value]
                    equip_ids_list.append(value)
                equip_ids_list = str(equip_ids_list)
                hero_player_dict[hero_sourcename].append(equip_ids_list)
            # print('添加23值索引后的英雄选手字典', hero_player_dict)

            # 选手的位置数据补充到hero_player_dict的值列表索引为24
            # 值存储为json格式,存储到skill_ids_list = []中
            for key, values in skill_ids_dict.items():
                skill_ids_list = []
                hero_sourcename = result[key]
                for value in values:
                    value = result[value]
                    skill_ids_list.append(value)
                    # print(111, skill_ids_list)
                hero_player_dict[hero_sourcename].append(skill_ids_list)
            # print('添加24值索引后的英雄选手字典', hero_player_dict)

            # 添加或插入到对局详情表中
            sql_battle_insert = "INSERT INTO `game_match_battle` (match_id, duration, index_num," \
            " status, type, team_a_kill_count, team_b_kill_count, team_a_death_count, team_b_death_count, " \
            "team_a_assist_count, team_b_assist_count, team_a_big_dragon_count, team_b_big_dragon_count, " \
            "team_a_small_dragon_count, team_b_small_dragon_count, team_a_tower_count, team_b_tower_count, win_team, " \
            "first_big_dragon_team, first_small_dragon_team, first_blood_team, team_a_five_kills, team_b_five_kills, " \
            "team_a_ten_kills, team_b_ten_kills, first_tower_team, team_a_money, team_b_money, " \
            "team_a_side, team_b_side, source_matchid, source_from) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, " \
            "{11}, {12}, {13}, {14}, {15}, {16}, '{17}', '{18}', '{19}', '{20}', '{21}',' {22}', '{23}', '{24}', '{25}', " \
            "{26}, {27}, '{28}', '{29}', {30}, '{31}') " \
                                "ON DUPLICATE KEY UPDATE " \
            "match_id = {0}, duration = {1}, index_num={2}, status = {3}, type = {4}, team_a_kill_count = {5}, " \
            "team_b_kill_count = {6}, team_a_death_count = {7}, team_b_death_count = {8}, team_a_assist_count = {9}, " \
            "team_b_assist_count = {10}, team_a_big_dragon_count = {11}, team_b_big_dragon_count = {12}, " \
            "team_a_small_dragon_count = {13}, team_b_small_dragon_count = {14}, team_a_tower_count = {15}, " \
            "team_b_tower_count = {16}, win_team = '{17}', first_big_dragon_team = '{18}', first_small_dragon_team = '{19}', " \
            "first_blood_team = '{20}', team_a_five_kills = '{21}', team_b_five_kills = '{22}', team_a_ten_kills = '{23}'," \
            "team_b_ten_kills = '{24}', first_tower_team = '{25}', team_a_money = {26}, team_b_money = {27}, " \
            "team_a_side = '{28}', team_b_side = '{29}', source_matchid={30}, source_from='{31}';".format(match_id, duration, index_num,
            status, types, team_a_kill_count, team_b_kill_count, team_a_death_count, team_b_death_count,
            team_a_assist_count, team_b_assist_count, team_a_big_dragon_count, team_b_big_dragon_count,
            team_a_small_dragon_count, team_b_small_dragon_count, team_a_tower_count, team_b_tower_count, win_team,
            first_big_dragon_team, first_small_dragon_team, first_blood_team, team_a_five_kills, team_b_five_kills,
            team_a_ten_kills, team_b_ten_kills, first_tower_team, team_a_money, team_b_money,  team_a_side, team_b_side,
            resultID, source)
            # print('记录对局详情表：', sql_battle_insert)
            db.update_insert(sql_battle_insert)
            # print('记录对局详情表插入完成')

            # 开始更新或插入选手表的数据
            # hero_player_dict的格式：
            # {‘hero_name’：['player_name', 'player_id', 'player_avatar', 'hero_id', 'kill_count', 'assist_count',
            # 'death_count', 'level_dict', 'avatar_dict', 'last_hit_dict', 'last_damage_dict', 'last_per_damage_dict',
            # 'last_damage_rate_dict', 'last_damage_taken_dict', 'last_per_damage_taken_dict',
            # 'last_damage_taken_rate_dict', 'kda_dict', 'money_count_dict', 'money_minute_dict', 'offered_rate_dict',
            # 'score_dict', 'position', 'equip_ids', 'skill_ids'],......}
            for key_player, value_player in hero_player_dict.items():
                # 英雄名是键
                hero_name = key_player
                # 值是其他字段
                player_name = value_player[0]
                player_id = value_player[1]
                player_avatar = value_player[2]
                hero_id = value_player[3]
                kill_count = value_player[4]
                assist_count = value_player[5]
                death_count = value_player[6]
                team_color = value_player[7]
                team_id = team_judge[team_color]
                hero_level = value_player[8]
                hero_avatar = value_player[9]
                last_hit_count = value_player[10]
                damage_count = value_player[11]
                damage_minute = value_player[12]
                damage_percent = value_player[13]
                damage_taken_count = value_player[14]
                damage_taken_minute = value_player[15]
                damage_taken_percent = value_player[16]
                kda = value_player[17]
                money_count = value_player[18]
                money_minute = value_player[19]
                offered_rate = value_player[20]
                score = value_player[21]
                position = value_player[22]
                equip_ids = value_player[23]
                # equip_ids = json.dumps(equip_ids)
                equip_ids = equip_ids.replace('\'', '\"')
                skill_ids = value_player[24]
                skill_ids = json.dumps(skill_ids)
                skill_ids = skill_ids.replace('\'', '\"')



                # 添加或修改选手对局记录
                sql_player_insert = "INSERT INTO `game_player_battle_record` (match_id, player_id, player_name, " \
                    "player_avatar, hero_id, hero_level, hero_name, hero_avatar, kill_count, death_count, assist_count," \
                    " last_hit_count, last_hit_minute, damage_count, damage_minute, damage_percent, damage_taken_count, " \
                    "damage_taken_minute, damage_taken_percent, kda, money_count, money_minute, offered_rate, score, " \
                    "equip_ids, skill_ids, position, type, source_matchid, team_id, source_from) VALUES({0}, {1}, '{2}', \"{3}\", " \
                    "{4}, {5}, '{6}', '{7}', {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, " \
                    "{20}, {21}, {22}, {23}, '{24}', '{25}', '{26}', {27}, {28}, {29}, '{30}') " \
                    "ON DUPLICATE KEY UPDATE match_id = {0}, player_name = '{2}', player_avatar = \"{3}\", " \
                    "hero_id = {4}, hero_level = {5}, hero_name = '{6}', hero_avatar = '{7}', kill_count = {8}, " \
                    "death_count = {9}, assist_count = {10}, last_hit_count = {11}, last_hit_minute = {12}, " \
                    "damage_count = {13}, damage_minute = {14}, damage_percent = {15}, damage_taken_count = {16}, " \
                    "damage_taken_minute = {17}, damage_taken_percent = {18}, kda = {19}, money_count = {20}, " \
                    "money_minute = {21}, offered_rate = {22}, score = {23}, equip_ids = '{24}', skill_ids = '{25}'," \
                    " position='{26}', type={27}, source_matchid={28}, team_id={29}, source_from='{30}';".format(match_id,
                    player_id, player_name, player_avatar, hero_id, hero_level, hero_name, hero_avatar, kill_count,
                    death_count, assist_count, last_hit_count, last_hit_minute, damage_count, damage_minute, damage_percent,
                    damage_taken_count, damage_taken_minute, damage_taken_percent, kda, money_count, money_minute,
                    offered_rate, score, equip_ids, skill_ids, position, types, resultID, team_id, source)
                # print('记录选手表：', sql_player_insert)
                db.update_insert(sql_player_insert)
                # print('记录选手表插入完成')




# 本周的比赛：form_data中的date参数为空
form_data['data'] = ''
parse(start_url, form_data, headers)
# print('----------------')
# 上周的比赛：form_data中的date参数为上周五的日期，例如：2020-07-26
form_data['date'] = last_friday_str
# print(form_data)
parse(start_url, form_data, headers)












