# -*-coding:utf-8-*-
from datetime import datetime
from common_tool import get_response, get_log, redis_check
from db.import_data_to_mysql import con_db
from db.import_data_to_redis import RedisCache_checkAPI
from setting import db_setting

"""
雷竞技网英雄联盟赔率爬虫
url: https://www.ray83.com/match/37198305
"""

leijingji_log = get_log('leijingji')
# 爬虫流程：
# 开始加载两页赛程的url：start_url， second_url
# start_url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'，
# second_url ='https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=2'
# 从start_url和second_url中拿到id，拼凑得到详情url
# 详情url中拿到对应赔率url：https://incpgameinfo.esportsworldlink.com/v2/odds?match_id=37219633

# 今日
start_url = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=2'

# 滚盘
gunpan_url1 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=1'
gunpan_url2 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=0'
gunpan_url3 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=0'
gunpan_urls = [gunpan_url1, gunpan_url2, gunpan_url3]

# 赛前
befor_url_1 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=3'
befor_url_2 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=3'
befor_url_3 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=3&match_type=3'
befor_url_4 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=4&match_type=3'
befor_url_5 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=5&match_type=3'
befor_url_6 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=6&match_type=3'
befor_url_7 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=7&match_type=3'
befor_url_8 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=8&match_type=3'
befor_url_9 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=9&match_type=3'

befor_url = [befor_url_1, befor_url_2, befor_url_3, befor_url_4, befor_url_5, befor_url_6, befor_url_7,
             befor_url_8, befor_url_9]

# 结束（此url进来的数据只用来更新win字段）
end_url1 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=1&match_type=4'
end_url2 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=2&match_type=4'
end_url3 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=3&match_type=4'
end_url4 = 'https://incpgameinfo.esportsworldlink.com/v2/match?page=4&match_type=4'

end_url = [end_url1, end_url2, end_url3, end_url4]

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
    '获胜者':1, '输赢':2, '地图让分':3, '获得一血':4, '谁先获得五杀':5,
    '摧毁第一座塔':7, '击杀第一条小龙':8, '谁先击杀第一只暴君':8, '击杀第一条大龙':9, '谁先击杀先知主宰':9, '杀敌总数单双':10, '杀敌总数大小':11
}

# 根据赔率类型判断是否与队伍相关，如果相关要关联队伍id（后端要用）(在bet_types_judge中的就与队伍相关)
bet_types_judge = [1, 2, 3, 4, 5, 7, 8, 9]

# 有盘口的赔率类型
bet_types_handicap = [3, 11, 12, 29]



# 网站存在有些title类型的竞猜接口不一定两两成对返还，有可能是返还四条数据（两条旧数据，两条新数据）
# 这样抓取的第三四条会覆盖第一二条造成问题，所以需要过滤掉其中的两条新数据（保留旧数据）
title_judge = ['地图让分']


# status状态对应：
# 0: 比赛尚未开始，正常更新    2: 结束   4: 封盘
# 雷竞技与表中对应关系：
# 1--0   4--4   2--4    5--2
bet_status = {
    1:0, 4:4, 2:4, 5:2
}

# 考虑到王者荣耀有bo7，且
match_stage_bo = {
    'final':0, 'r1':1, 'r2':2, 'r3':3, 'r4':4, 'r5':5, 'r6':6, 'r7':7
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
        try:
            game_name = response['game_name']
            leagueName = response['tournament_name']
            # print('联赛名称:',game_name, leagueName)
            # 过滤只拿到英雄联盟的赔率（LPL, LCK, LCS, LEC, LDL）

            if game_name == '王者荣耀' or (game_name == '英雄联盟' and ('LPL' in leagueName or 'LCK' in leagueName or 'LCS'
                                                    in leagueName or 'LEC' in leagueName or 'LDL' in leagueName )):
                # 有个lplol的需要过滤
                if 'LPLOL' not in leagueName:
                    types = game_type[game_name]
                    id = response['id']
                    # print('网站的赛事id：',id)
                    match_url = match_url_start + str(id)
                    # print('详情赔率url:', match_url)
                    responses_detail = get_response(match_url, headers)
                    responses_detail = responses_detail['result']
                    # print('详情数据：', responses_detail)
                    match_name = response['match_name']
                    match_name = match_name.split(' - VS - ')
                    source_a_name = match_name[0]
                    source_b_name = match_name[1]
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

                    # 先查找redis的zset集合中有没有对应网站的source_matchid，没有就添加
                    # print('查找前的数据:', leagueName, source_a_name, source_b_name, start_time)
                    result = redis_check(redis, game_name, db, source, leagueName, source_matchid, source_a_name,
                                         source_b_name, start_time)
                    # print(result)
                    if result:
                        match_id = result[0]
                        if match_id:
                            sql_insert = 'update game_python_match set bet_id={0} where id={1}'.format(id, match_id)
                            # print(sql_insert)
                            db.update_insert(sql_insert)
                            # print('记录bet_id字段完成')
        except Exception as e:
            leijingji_log.error(e, exc_info=True)


                # result = redis_check(redis, game_name, db, source, leagueName, source_matchid, source_a_name, source_b_name, start_time)
                # print('match_id:', result, source_a_name, source_b_name)
                # # 如果match_id为空，说明雷竞技的竞猜赛程在赛程表中没找到，这时不录入
                # if result:
                #     match_id = result[0]
                #     team_a_id = result[2]
                #     team_b_id = result[3]
                #     # 0-139条赔率数据，每两组构成一条数据库中的数据
                #     # print(type(responses_detail['odds']), responses_detail['odds'])
                #
                #     option_one_name = 'Null'
                #     option_two_name = 'Null'
                #     option_one_odds = 'Null'
                #     option_two_odds = 'Null'
                #     option_one_team_id = 'Null'
                #     option_two_team_id = 'Null'
                #     # odds中的数据两两拼成一条完整竞猜数据,用count的状态来判断添加到哪一个字段
                #     count = True
                #
                #     # 地图让分的赔率抓取比较复杂，由于网站出现多种，要进行取舍
                #     # 暂定规则如下：
                #     # 1.英雄联盟：拿到最开始的地图让分，后面出现新的也不要
                #     # 2.王者荣耀：由于bo比较多，拿到
                #     # 计算地图让分出现次数，过滤掉新数据
                #     judge_exclude_dtrf = 0
                #     # 列表计数
                #     list_count = 0
                #     # 假数据的索引列表
                #     list_index = []
                #     # 判断title_judge中的玩法是否超出两条数据，超出就过滤后来的新数据（status为1）
                #     #目前网站上只有‘地图让分’有新旧数据的存在（保留旧数据）
                #     for rate_message in responses_detail['odds']:
                #         if rate_message['group_name'] == '地图让分':
                #             judge_exclude_dtrf += 1
                #             if rate_message['status'] == 1:
                #                 list_index.append(list_count)
                #         list_count += 1
                #     # print('新数据列表索引:', list_index)
                #     responses_detail_list = responses_detail['odds']
                #     # print('去除假数据之前：', len(responses_detail_list), responses_detail_list)
                #     # 存在更新新数据情况时，根据新数据的索引列表去掉接口返回列表的新数据
                #     if judge_exclude_dtrf > 2:
                #         responses_detail_list = [responses_detail_list[i] for i in range(len(responses_detail_list)) if (i not in list_index)]
                #     # print('去除新数据之后：', len(responses_detail_list), responses_detail_list)
                #
                #
                #     # 接口数据整理完，开始第二次遍历入库
                #     for rate_message in responses_detail_list:
                #         # print('odds详情:', rate_message)
                #         title = rate_message['group_name']
                #         # match_stage: r1为第一局  r2为第二局...   final为整个大局
                #         match_stage = rate_message['match_stage']
                #         board_num = match_stage_bo[match_stage]
                #         # 暂时只要bet_type中的竞猜项目
                #         if title in bet_types:
                #
                #             # 将title为地图让分的标题更正为全场让分
                #             title = '全场让分' if rate_message['group_name'] == '地图让分' else rate_message['group_name']
                #             bet_type =3 if  title == '全场让分' else bet_types[title]
                #             # ’获胜者‘的match_stage不为final，bet_type改为‘输赢’
                #             if title == '获胜者' and match_stage != 'final':
                #                 bet_type = 2
                #             # 不知道是否保留所以先给0
                #             end_time = 0
                #             source_status = rate_message['status']
                #             if source_status in bet_status:
                #                 status = bet_status[source_status]
                #                 # print('详细竞猜数据:', title, match_stage, source_status, status)
                #                 if count:
                #                     option_one_name = rate_message['name']
                #                     option_one_odds = rate_message['odds']
                #                     win_one = rate_message['win']
                #                     id_one = rate_message['id']
                #                     handicap_one = rate_message['value'] if bet_type in bet_types_handicap else 'null'
                #                     if bet_type in bet_types_judge:
                #                         option_one_team_id = team_a_id if source_a_name in option_one_name  else team_b_id
                #                     else:
                #                         option_one_team_id = 'null'
                #                     count = False
                #                     # 如果存在status为4的赔率，过滤掉
                #                 else:
                #                     option_two_name = rate_message['name']
                #                     option_two_odds = rate_message['odds']
                #                     win_two = rate_message['win']
                #                     id_two = rate_message['id']
                #                     handicap_two = rate_message['value'] if bet_type in bet_types_handicap else 'null'
                #                     if bet_type in bet_types_judge:
                #                         # option_two_name 中带名
                #                         option_two_team_id = team_b_id if source_b_name in option_two_name  else team_a_id
                #                     else:
                #                         option_two_team_id = 'null'
                #                     count = True
                #
                #                 # 添加竞猜数据的记录
                #                 if count and match_id != None:
                #                     # 盘口数据根据id小的判断，id小的为主队
                #                     handicap = handicap_one if id_one < id_two else handicap_two
                #                     win = win_one if id_one < id_two else win_two
                #                     # print(win)
                #                     if handicap != 'null':
                #                         handicap = '\'' + handicap + '\''
                #                     # print('核对两队名称:', option_one_name, option_one_team_id, source_a_name, option_two_name,
                #                     #       option_two_team_id, source_b_name)
                #
                #                     # print('竞猜双方信息:', count, option_one_name, source_a_name, option_one_odds, option_one_team_id,
                #                     #       option_two_name, source_b_name, option_two_odds, option_two_team_id)
                #                     if judge == 1:
                #                         sql_bet_insert = "INSERT INTO `game_bet_info_copy` (type, source, source_matchid, match_stage," \
                #                             " match_id, board_num, title, bet_type, end_time, status, handicap, option_one_name, " \
                #                             "option_two_name, option_one_odds, option_two_odds, option_one_team_id, option_two_team_id, win, source_status) " \
                #                                 "VALUES({0}, '{1}', '{2}', '{3}', {4}, {5}, '{6}', {7}, {8}, {9}, {10}, '{11}', '{12}'," \
                #                                 " {13}, {14}, {15}, {16}, {17}, {18}) " \
                #                                             "ON DUPLICATE KEY UPDATE " \
                #                             "type={0}, source='{1}', match_id={4}, board_num={5}, title='{6}', bet_type={7}, end_time={8}," \
                #                             " status={9}, handicap={10}, option_one_name='{11}', option_two_name='{12}', " \
                #                             "option_one_odds={13}, option_two_odds={14}, option_one_team_id={15}, " \
                #                             "option_two_team_id={16}, win={17}, source_status={18};".format(types, source, id,
                #                             match_stage, match_id, board_num, title, bet_type, end_time, status, handicap,
                #                             option_one_name, option_two_name, option_one_odds, option_two_odds,
                #                             option_one_team_id, option_two_team_id, win, source_status)
                #
                #                         # print('记录竞猜表更新或插入：', sql_bet_insert)
                #                         db.update_insert(sql_bet_insert)
                #                         # print('记录竞猜表更新或插入完成')
                #                     else:
                #                         sql_searchid = "select id from game_bet_info_copy where source_matchid={0} and" \
                #                                        " title='{1}' and match_stage='{2}';".format(source_matchid, title, match_stage)
                #                         # 找到已经更新的赔率，在已结束的接口中更新win字段
                #                         # print('找到需要更新win字段的赔率id:', sql_searchid)
                #                         bet_id = db.select_id(sql_searchid)
                #                         if bet_id:
                #                             sql_bet_update_win = "update game_bet_info_copy set win={0} where id={1};".format(win, bet_id)
                #                             # print('记录竞猜表只更新win字段：', bet_id, sql_bet_update_win)
                #                             db.update_insert(sql_bet_update_win)
                #                             # print('记录竞猜表只更新win字段完成')





# print('今日赔率',start_url)
parse(start_url, headers)
# print('今日赔率抓取完成')

# print('滚盘赔率',gunpan_url1)
for gunpan_url in gunpan_urls:
    parse(gunpan_url, headers)
# print('滚盘赔率抓取完成')

# print('赛前赔率',befor_url)
for url in befor_url:
    parse(url, headers)
# print('赛前赔率抓取完成')

