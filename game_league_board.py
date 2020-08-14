# -*-coding:utf-8-*-

from common_tool import post_response, get_response, api_check, API_return_200, get_log
from import_data_to_redis import RedisCache_checkAPI
from import_data_to_mysql import con_db
from setting import db_setting
from datetime import datetime

"""
联赛积分榜（英雄联盟，王者荣耀在一张表）
抓取规则：
从start_url中post请求获取每个联赛的id
过滤掉一些后台没有的联赛（league_unknow列表）
有联赛id拼接出常规赛，季后赛赛程 ：https://img1.famulei.com/tr/{联赛id}.json?_=1594797795974
从常规赛，季后赛赛程获取每周（小组）的id，拼接出这周（这组）比赛的赛果（过滤掉未进行的）
算出该赛程到目前为止，每个队伍的输赢数，净积分（小场赢一场积1分，输一场扣1分）
"""

start_url = 'https://www.scoregg.com/services/api_url.php'

header = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

league_unknow = ['2020 LCK夏季升降级赛', '2019KeSPA杯', '2019拉斯维加斯全明星', 'LPL公开训练赛', '2017 KPL秋季赛']
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

# 联赛阶段url
rank_url_pre = 'https://img1.famulei.com/tr/{0}.json?_={1}'
# 赛程列表url
match_url_pre = 'https://img1.famulei.com/tr_round/{0}.json?_={1}'
# 战队排名url
type_url_pre = 'https://img1.famulei.com/match/teamrank/{0}.json?_={1}'

# 此时的时间戳
now_time_match = datetime.now()
timestamps_match = int(now_time_match.timestamp() * 1000)

source = 'score'

# 键值对：‘网站战队名：分组名’
team_type_name = {}
# 键值对：‘后端返回战队名：分组名’
realteam_type_name = {}

league_board_log = get_log('league_board')
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])
redis = RedisCache_checkAPI()



def parse(form_data_yxlm, types):
    game_name = '英雄联盟' if types == 1 else '王者荣耀'
    league_id = 0
    try:
        responses = post_response(start_url, form_data_yxlm, header)
        responses = responses['data']['list']
        # print('源数据：', responses)
        for response in responses:
            # 拿到联赛id
            tournamentID = response['tournamentID']
            source_league_name = response['name']
            # 在未知联赛列表中就过滤掉
            if source_league_name in league_unknow:
                continue
            # 13位时间戳
            # source_league_name = '2020 LCS夏季赛'
            # tournamentID = '170'
            now_time = datetime.now()
            timestamps = int(now_time.timestamp() * 1000)
            # 先遍历拿到每个队伍的分组名称(分组名称在不同的联赛阶段是不变的)
            type_url = type_url_pre.format(tournamentID, timestamps)
            type_responses = get_response(type_url, header)
            type_responses = type_responses['data']
            for type_response in type_responses:
                source_team_name = type_response['team_name']
                group_name = type_response['group_name']
                # 没有规定分组显示积分榜
                team_type_name[source_team_name] = group_name if group_name else '积分榜'
            # print('分组情况:', team_type_name)

            rank_url = rank_url_pre.format(tournamentID, timestamps)
            # print(rank_url, response)
            match_responses = get_response(rank_url, header)
            # 再遍历拿到每个联赛阶段的id用于凭借更加细致的赛程列表
            for match_response in match_responses:
                stage = match_response['name']
                round_son = match_response['round_son']
                roundID = match_response['roundID']
                # print('联赛阶段信息：', stage, round_son, roundID)

                # 用于统计每个联赛阶段胜负场次，净胜积分
                team_win_count = {}
                team_lose_count = {}
                team_score_count = {}
                # 如果round_son有值，遍历去取‘round_son’中的id拼接赛程列表（在网页上的体现就是有更细一层的划分，类似于周几的赛程）
                if round_son:
                    for match_list in round_son:
                        id = match_list['id']
                        # 拿到每周（每组）赛事列表的id,遍历合并每周（每组）的 胜/负/净胜分
                        # print('计算积分之前的数据:', game_name, source_league_name, team_win_count, team_lose_count, team_score_count,
                        #       id)
                        # 拼接赛程列表url
                        match_url = match_url_pre.format(id, timestamps_match)
                        match_details = get_response(match_url, header)
                        for match_detail in match_details:
                            result_detail = parse_detail(match_detail, game_name, source_league_name, team_win_count,
                                                  team_lose_count, team_score_count)
                            if result_detail:
                                league_id = result_detail

                                # 如果round_son为空，直接用‘p_’+ 'roundID'拼接赛程列表（在网页上的体现就是该联赛阶段只有一组赛程）
                else:
                    id = 'p_{}'.format(roundID)
                    # 拿到每周（每组）赛事列表的id,遍历合并每周（每组）的 胜/负/净胜分
                    # 拼接赛程列表url
                    match_url = match_url_pre.format(id, timestamps_match)
                    match_details = get_response(match_url, header)
                    for match_detail in match_details:
                        result_detail = parse_detail(match_detail, game_name, source_league_name, team_win_count,
                                                 team_lose_count, team_score_count)
                        if result_detail:
                            league_id = result_detail

                # print('拿到的联赛阶段统计结果：', league_id, '胜', team_win_count, '负', team_lose_count, '净胜分', team_score_count)
                # 联赛阶段的积分数据已统计完，遍历更新或插入到表中
                # 字典的键：‘team_a_name’+ ‘+’ + ‘team_b_id’
                # 理论上 team_win_final， team_lose_final， team_score_final的长度一样
                for key, value in team_win_count.items():
                    team_name = key.split('+')[0]
                    team_id = key.split('+')[1]
                    win_count = value
                    lost_count = team_lose_count[key]
                    score = team_score_count[key]
                    # 从分组字典中找到队伍的对应分组
                    type_name = realteam_type_name[team_name]

                    # 拿到该联赛阶段的 胜/负/净胜分后，开始更新后插入到表中
                    sql_rank = "INSERT INTO `game_league_board` (league_id, team_id, win_count, lost_count, score, type_name, stage," \
                               " type, team_name)  VALUES('{0}', '{1}', {2}, {3}, {4}, '{5}', '{6}', {7}, '{8}') " \
                                    " ON DUPLICATE KEY UPDATE " \
                               "league_id='{0}', team_id='{1}', win_count={2}, lost_count={3}, score={4}, type_name='{5}', " \
                               "stage='{6}', type={7}, team_name='{8}';".format(league_id, team_id, win_count, lost_count, score,
                               type_name, stage, types, team_name)
                    # print('更新或插入排行表：', sql_rank)
                    db.update_insert(sql_rank)
                    # print('更新完成')
    except Exception as e:
        league_board_log.error('每组队局之前的异常')
        league_board_log.error(e, exc_info=True)


# 计算每个联赛阶段单周（单组）战队的胜，负，净胜分
def parse_detail(match_detail, game_name, source_league_name, team_win_count, team_lose_count, team_score_count):
    try:
        status = match_detail['status']
        team_a_win = int(match_detail['team_a_win'])
        team_b_win = int(match_detail['team_b_win'])
        # lck中sp战队和sho战队是一个队伍，统一称呼为sho
        source_team_a_name = 'SP' if match_detail['team_short_name_a'] == 'SHO' else match_detail['team_short_name_a']
        source_team_b_name = 'SP' if match_detail['team_short_name_b'] == 'SHO' else match_detail['team_short_name_b']
        if source_team_a_name == 'TBD' or source_team_b_name == 'TBD':
            return None
        else:
            team_type_name_a = team_type_name[source_team_a_name]
            team_type_name_b = team_type_name[source_team_b_name]

            # 只统计完成的赛事
            if status == '2':
                # 访问后端接口拿到联赛和两个战队id(因为一天更新一次，不用存入redis)
                result = api_check(game_name, source_league_name, source_team_a_name, source_team_b_name)
                # print('访问后端的结果:', result)
                if result['code'] == 600:
                    result = result['result']
                    league_id = result['league_id']
                    league_name = result['league_name']
                    team_a_id = result['team_a_id']
                    team_a_name = result['team_a_name']
                    team_b_id = result['team_b_id']
                    team_b_name = result['team_b_name']
                    realteam_type_name[team_a_name] = team_type_name_a
                    realteam_type_name[team_b_name] = team_type_name_b

                    # 从字典中取出合计的值，然后遍历计算，没有找到对应队伍就预设为0,字典的键：‘team_a_name’+ ‘+’ + ‘team_b_id’
                    key_a = team_a_name + '+' + team_a_id
                    key_b = team_b_name + '+' + team_b_id
                    team_score_count[key_a] = 0 if team_score_count.get(key_a) == None else \
                        team_score_count.get(key_a)
                    team_score_count[key_b] = 0 if team_score_count.get(key_b) == None else \
                        team_score_count.get(key_b)
                    team_win_count[key_a] = 0 if team_win_count.get(key_a) == None \
                        else team_win_count.get(key_a)
                    team_win_count[key_b] = 0 if team_win_count.get(key_b) == None \
                        else team_win_count.get(key_b)
                    team_lose_count[key_a] = 0 if team_lose_count.get(key_a) == None \
                        else team_lose_count.get(key_a)
                    team_lose_count[key_b] = 0 if team_lose_count.get(key_b) == None \
                        else team_lose_count.get(key_b)
                    # 净胜分：小场赢一场+1，输一场-1
                    team_score_count[key_a] = team_score_count[key_a] + team_a_win - team_b_win
                    team_score_count[key_b] = team_score_count[key_b] + team_b_win - team_a_win
                    # print('净胜分：', team_score_count[team_a_name], team_score_count[team_b_name])
                    # team_win_count中保存着键值对：  ‘战队名’:胜场
                    # team_lose_count中保存着键值对： ‘战队名’:负场
                    if team_a_win > team_b_win:
                        team_win_count[key_a] = team_win_count.get(key_a) + 1
                        team_lose_count[key_b] = team_lose_count.get(key_b) + 1
                    else:
                        team_win_count[key_b] = team_win_count.get(key_b) + 1
                        team_lose_count[key_a] = team_lose_count.get(key_a) + 1
                    # print('计算的数据为：', team_a_name, team_a_win, team_b_name, team_b_win)

                    return league_id
                elif result['code'] == 200:
                    # 判断为200就将不存在的添加到‘api_check_200’表中,让后端完善赛事名称(只添加返回的id为0的,不为0就是None)
                    API_return_200(db, result)
                    return None
            else:
                return None
    except Exception as e:
        league_board_log.error('计算胜/负/净胜分异常')
        league_board_log.error(e)

parse(form_data_yxlm, 1)
# print('英雄联盟抓取完成')
parse(form_data_wzry, 2)
# print('王者荣耀抓取完成')

