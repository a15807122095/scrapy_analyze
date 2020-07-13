# -*-coding:utf-8-*-
import time
import requests
from datetime import datetime, timedelta
from common_tool import get_response, redis_check
from lxml import etree
from common_tool import api_check
from import_data_to_mysql import con_db
from import_data_to_redis import RedisCache_checkAPI
from setting import db_setting

"""
雷竞技网英雄联盟赔率爬虫
url: https://www.ray83.com/match/37198305
"""
# 爬虫流程：
# 开始加载两页赛程的url：start_url， second_url
# start_url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'，
# second_url ='https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=2'
# 从start_url和second_url中拿到id，拼凑得到详情url
# 详情url中拿到对应赔率url：https://incpgameinfo.esportsworldlink.com/v2/odds?match_id=37219633

start_url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'
second_url ='https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=2'

match_url_start = 'https://incpgameinfo.esportsworldlink.com/v2/odds?match_id='

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

# 创建数据库对象
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])
# 创建redis对象
redis = RedisCache_checkAPI()
# 竞猜类型
# 1: 全场获胜；2: 输赢（单局）；3: 让分；4: 1血； 5: 5杀；6: 10杀；7: 首塔；8: 小龙首杀；9: 大龙首杀；10: 人头总数单双；
# 11: 总击杀数大小；12: 比赛时长大小；13：五分钟内是否出现1血；14：击杀数最多；15：第一条小龙元素为；16：第一条小龙元素为“水”；
# 17：第一条小龙元素为”土“ ；18： 第X局 第一条小龙元素为”火“；19：第X局 第一条小龙元素为”风“；20：小龙总击杀单双；21：首杀峡谷先锋；
# 22：十四分钟内是否摧毁首塔；23：摧毁防御塔总数大小；24：摧毁防御塔总数单双；25：哪支队伍首先摧毁水晶兵营；26：10分钟总击杀；
# 27：20分钟总击杀；28：全场正确比分；29：全场地图总数大小'

# 雷竞技目前有的竞猜项目为以下，后面出现另外的再补充（获胜者如果是小局就改为输赢）
bet_types = {
    '获胜者':1, '输赢':2, '地图让分':3, '杀敌数让分':3, '获得一血':4, '哪个位置获得一血':4, '哪个位置交出一血':4, '谁先获得五杀':5,
    '谁先获得十杀':6, '摧毁第一座塔':7, '击杀第一条小龙':8, '击杀第一条大龙':9, '杀敌总数单双':10, '杀敌总数大小':11,  '时间大小':12,
    '第一条元素龙属性为':15, '首杀峡谷迅捷蟹':21, '摧毁塔总数单双':24, '地图总数大小':29
}

# status状态对应：
# 0: 比赛尚未开始，正常更新   1: 比赛开始进行，停止更新(早盘)，正常更新(滚球)   2: 结束   4: 封盘
# 雷竞技与表中对应关系：
# 1--0   4--1   2--4    5--2
bet_status = {
    1:0, 4:1, 2:4, 5:2
}

game_type = {
    '英雄联盟':1,
    '王者荣耀':2
}

def parse(url, headers):
    responses = get_response(url, headers)
    responses = responses['result']
    # print('源数据：', len(responses))
    source = '雷竞技'
    for response in responses:
        game_name = response['game_name']
        leagueName = response['tournament_name']
        # print('联赛名称:',game_name, leagueName)
        # 过滤只拿到英雄联盟的赔率（LPL, LCK, LCS, LEC, LDL）
        if game_name == ('英雄联盟' or '王者荣耀') and ('LPL' in leagueName or 'LCK' in leagueName or 'LCS' in leagueName
                                    or 'LEC' in leagueName or 'LDL' in leagueName ):
            types = game_type[game_name]
            id = response['id']
            # print('网站的赛事id：',id)
            match_url = match_url_start + str(id)
            # print('详情赔率url:', match_url)
            responses_detail = get_response(match_url, headers)
            responses_detail = responses_detail['result']
            # print('详情数据：', responses_detail)
            bo = responses_detail['round'][-1:]
            board_num = int(bo)

            source_a_name = response['team'][0]['team_name']
            source_b_name = response['team'][1]['team_name']
            start_time = response['start_time']
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            leagueName_pre = str(start_time.year) + ' '
            # 雷竞技的联赛名不带年份，要自己加上去，用比赛的年份判断出那一年再拼接上去
            # 例如 start_time:'2020-07-08' ---'2020 ' + leagueName
            leagueName = leagueName_pre + leagueName
            # print('leagueName:',leagueName)
            start_time = int(start_time.timestamp())
            start_time = str(start_time)
            source_matchid = str(id)
            result = redis_check(redis, db, source, leagueName, source_matchid, source_a_name, source_b_name, start_time)
            # print('match_id:', result, source_a_name, source_b_name)

            # 如果match_id为空，说明雷竞技的竞猜赛程在赛程表中没找到，这时不录入
            if result:
                match_id = result[0]
                team_a_id = result[1]
                team_b_id = result[2]
                # 0-139条赔率数据，每两组构成一条数据库中的数据
                # print(type(responses_detail['odds']), responses_detail['odds'])

                # odds中的数据两两拼成一条完整竞猜数据,用count的状态来判断添加到哪一个字段
                count = True
                option_one_name = 'Null'
                option_two_name = 'Null'
                option_one_odds = 'Null'
                option_two_odds = 'Null'
                option_one_team_id = 'Null'
                option_two_team_id = 'Null'
                for rate_message in responses_detail['odds']:
                    title = rate_message['group_name']
                    # match_stage: r1为第一局  r2为第二局...   final为整个大局
                    match_stage = rate_message['match_stage']
                    # 暂时只要bet_type中的竞猜项目
                    if title in bet_types:
                        bet_type = bet_types[title]
                        # ’获胜者‘的match_stage不为final，bet_type改为‘输赢’
                        if title == '获胜者' and match_stage != 'final':
                            bet_type = 2
                        # 不知道是否保留所以先给0
                        end_time = 0
                        source_status = rate_message['status']
                        if source_status in bet_status:
                            status = bet_status[source_status]
                            handicap = rate_message['value']
                            # print('详细竞猜数据:', title, match_stage, source_status, status, handicap)
                            if count:
                                option_one_name = rate_message['name']
                                option_one_odds = rate_message['odds']
                                if option_one_name == source_a_name:
                                    option_one_team_id = team_a_id
                                elif option_one_name == source_b_name:
                                    option_one_team_id = team_b_id
                                else:
                                    option_one_team_id = 'Null'
                                count = False
                            else:
                                option_two_name = rate_message['name']
                                option_two_odds = rate_message['odds']
                                if option_two_name == source_b_name:
                                    option_two_team_id = team_b_id
                                elif option_two_name == source_a_name:
                                    option_two_team_id = team_a_id
                                else:
                                    option_two_team_id = 'Null'
                                count = True
                            # 添加竞猜数据的记录
                            if count and match_id != None:
                                # print('竞猜双方信息:', count, option_one_name, source_a_name, option_one_odds, option_one_team_id,
                                #       option_two_name, source_b_name, option_two_odds, option_two_team_id)
                                sql_bet_insert = "INSERT INTO `game_bet_info_copy` (type, source, source_matchid, match_stage," \
                                    " match_id, board_num, title, bet_type, end_time, status, handicap, option_one_name, " \
                                    "option_two_name, option_one_odds, option_two_odds, option_one_team_id, option_two_team_id) " \
                                        "VALUES({0}, '{1}', '{2}', '{3}', {4}, {5}, '{6}', {7}, {8}, {9}, '{10}', '{11}', '{12}'," \
                                        " {13}, {14}, '{15}', '{16}') " \
                                                    "ON DUPLICATE KEY UPDATE " \
                                    "type={0}, source='{1}', match_id={4}, board_num={5}, title='{6}', bet_type={7}, end_time={8}," \
                                    " status={9}, handicap='{10}', option_one_name='{11}', option_two_name='{12}', " \
                                    "option_one_odds={13}, option_two_odds={14}, option_one_team_id='{15}', " \
                                    "option_two_team_id='{16}';".format(types, source, id, match_stage, match_id, board_num, title,
                                    bet_type, end_time, status, handicap, option_one_name, option_two_name, option_one_odds,
                                    option_two_odds, option_one_team_id, option_two_team_id)
                                # print('记录竞猜表：', sql_bet_insert)
                                db.update_insert(sql_bet_insert)
                                # print('记录竞猜表插入完成')


parse(start_url, headers)
# parse(second_url, headers)

