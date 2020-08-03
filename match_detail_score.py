# -*-coding:utf-8-*-
import json
import requests
from common_tool import post_response, get_log, get_weeks, get_response, redis_check, \
    player_check, api_return_200, hero_check
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_checkAPI
from datetime import datetime, timedelta
from setting import db_setting


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
    try:
        results = post_response(url, data, headers)
        results = results['data']['list']
        print('需要拿的赛程日期:', date_list)
        print(len(results), type(results), results)
        for key_list, results_list in results.items():
            # 排除掉今天和昨天之外的赛程
            if key_list not in date_list:
                continue
            result_list = results_list['info']
            print('所有赛程:', key_list, type(result_list), result_list)
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
                    print('得到的时间：', start_time_str, start_time_date, detail_list)
                    if detail_list:
                        # 以detail_list中遍历次数计为bo
                        index_num = 1
                        for resultID in detail_list:
                            resultID = resultID['resultID']
                            detail_urls = detail_url.format(resultID, now_date_stamp)
                            print('详情url：', resultID, detail_urls)
                            detail_parse(detail_urls, source_matchid, types, index_num, game_name, league_name, start_time, headers)
                            index_num += 1
    except Exception as e:
        match_detail_score_log.error(e)



def detail_parse(url, source_matchid, types, index_num, game_name, league_name, start_time, headers):
    result_all = get_response(url, headers)
    source = 'score'

    if result_all:
        # 将选手信息与英雄信息以键值对的形式存到字典中 ,
        # 字典形式:‘hero_name’：['player_name','player_id','hero_id']
        # 例如：{ ‘荒漠屠夫’：['bin','player_id','hero_id'],......}
        team_result = result_all['data']['teams']
        hero_player_dict = {}
        for player_result in team_result:
            # 选手id需要跟后端匹配拿到正确的player_id
            player_name = player_result['player_name']
            # 先从redis中找到player_id，有记录代表之前已记录,取出player
            # redis存储结构：（源+player+player_name:player_id）‘score+player+uzi:'123'
            key_player = source + '+' + 'player' + '+' + player_name
            result = redis.get_data(key_player)
            # print('redis查询player的结果：', result)
            if result:
                player_id = result
            else:
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
                        # print('redis记录player完成：', key_hero, hero_id)
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
                    hero_player_dict['hero_name'] = [player_name, player_id, hero_id]
        print('英雄选手字典:', hero_player_dict)

        result = result_all['data']['result_list']
        # 先暂且把蓝方当主队，红方当客队请求后端拿到规范后的队名
        home_team = result['blue_name']
        guest_name = result['red_name']
        # redis中加入网站源标记
        source = 'SN网站'
        game_name = '英雄联盟'
        result_check = redis_check(redis, game_name, db, source, league_name, source_matchid, home_team, guest_name, start_time)
        match_id = result_check[0]
        # match_id, league_id, team_a_id, tea_b_id, team_a_name, tea_b_name, league_name
        # 后端返回600且match_id不为空，说明对局详情在赛程表中匹配到赛程
        if result_check and match_id:
            # 网站的比赛时长有个‘game_time_m’代表分钟，‘game_time_s’代表秒
            duration = result['game_time_m']*60 + result['game_time_s']
            status = 1
            team_a_name = result[4]
            team_b_name = result[5]
            sql_check = 'select team_a_name and team_b_name from game_python_match where id = {}'.format(match_id)
            result_team = db.select_id(sql_check)
            # 正常情况下网站的a,b队就是表中的a，b队
            # 如果score网站的a（蓝），b（红）队校正后与表中a,b队相反，以表为准，此时score的b队是主队
            judge_reversal = False
            print(team_a_name, result_team[1], team_b_name, result_team[0])
            if team_a_name == result_team[1] and team_b_name == result_team[0]:
                judge_reversal = True
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

            # 选手的数据























# # 本周的比赛：form_data中的date参数为空
# form_data['data'] = ''
# parse(start_url, form_data, headers)
# print('----------------')
# 上周的比赛：form_data中的date参数为上周五的日期，例如：2020-07-26
form_data['date'] = last_friday_str
print(form_data)
parse(start_url, form_data, headers)












