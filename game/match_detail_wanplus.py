# -*-coding:utf-8-*-

import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')

from common_tool import post_response, redis_check, get_weeks, redis_check_playerID, redis_check_heroID
from import_data_to_redis import RedisCache_checkAPI
from import_data_to_mysql import con_db
from datetime import datetime
from setting import db_setting, chrome_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import requests, re, time

"""
王者荣耀赛事详情爬虫
从玩加网站上抓取 # https://www.wanplus.com 
抓取流程(静态资源):
先抓取王者荣耀赛程,从赛程拿到网站的对局id,拼凑出对局详情url: https://www.wanplus.com/schedule/65121.html
用xpath拿到每场小局的小局id,拼凑出每场小局详情的url:https://www.wanplus.com/match/68909.html#data
用xpath拿到详情数据入库
"""

start_url_wanplus = 'https://www.wanplus.com/ajax/schedule/list'

match_detail_url = 'https://www.wanplus.com/schedule/{}.html'

match_more_detail_url = 'https://www.wanplus.com/match/{}.html#data'

player_avater = 'https://static.wanplus.com/data/kog/player/{}_mid.png'

hero_avater = 'https://static.wanplus.com/data/kog/hero/square/{}.png'

headers_wanplus= {
'authority': 'www.wanplus.com',
'method': 'POST',
'path': '/ajax/schedule/list',
'scheme': 'https',
'accept': 'application/json, text/javascript, */*; q=0.01',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9',
'content-length': '43',
'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
'cookie': 'wanplus_token=f4f5aa3f18cc3119abe8cdabc5a7cebe; wanplus_storage=lf4m67eka3o; wanplus_sid=9e696f0029946fb2c4f9a8b7c523c370; UM_distinctid=172ff8aed371e-009aa63dd252d6-4353760-e1000-172ff8aed38670; wp_pvid=5917824012; gameType=2; wanplus_csrf=_csrf_tk_806653903; wp_info=ssid=s8611067605; Hm_lvt_f69cb5ec253c6012b2aa449fb925c1c2=1593425195,1593479359; isShown=1; CNZZDATA1275078652=1155513258-1593421357-%7C1593480701; Hm_lpvt_f69cb5ec253c6012b2aa449fb925c1c2=1593485299',
'origin': 'https://www.wanplus.com',
'referer': 'https://www.wanplus.com/lol/schedule',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
'x-csrf-token': '806653903',
'x-requested-with': 'XMLHttpRequest'
}



# 构建selenium对象
chrome_options = Options()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_path)

#得到上周的日期和这周到今天的日期字符串列表：
# 将工具函数中的 ['2020.08.05', '2020.08.04', '2020.08.03', '2020.08.02']转换成
# ['20200805', '20200804', '20200803', '20200802']
date_list = get_weeks()
date_lists = []

for date in date_list:
    date = re.sub(r'[^0-9]+','',date)
    date_lists.append(date)
# print(date_lists)

# 玩加网站的post参数主要拿time，上周为周日的00：00:00的时间戳，本周和下周为周1的00:00:00时间戳
# 应该是点击上周就以上周日00:00:00的时间戳为time，点击下周就以下周1的00:00:00的时间戳为time

today = datetime.now()
week_day = today.weekday()
today_str = today.strftime('%Y-%m-%d 00:00:00')
str_today = datetime.strptime(today_str, '%Y-%m-%d %H:%M:%S')
today_stamp = str_today.timestamp()
# 这周1的00:00:00时间戳
monday_stamp = int(today_stamp - 86400 * week_day)
# # 上周日的00:00:00时间戳
last_weekstamp = int(monday_stamp - 86400)

# match_detail_wanplus_log = get_log('match_detail_wanplus')

redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse_wanplus(url, data, db, headers):
    # try:
    responses = post_response(url, data, headers)
    results = responses['data']['scheduleList']
    game_name = '王者荣耀'
    source_from = 'wanplus王者荣耀详情'  # 爬虫源网站
    types = 2
    status = 1
    for key_list, result in results.items():
        if key_list not in date_lists:
            continue
        date_time = result['time']
        results_match = result['list']
        # 有的字段是bool类型，过滤掉
        # print(results_match)
        if type(results_match) == bool:
            continue
        for result_match in results_match:
            source_matchid = result_match['scheduleid']
            # print(source_matchid)
            league_name = result_match['ename']
            home_team = result_match['oneseedname']
            guest_name = result_match['twoseedname']
            # print('赛程信息：', league_name, home_team, guest_name)
            # 源数据中的start_time为‘17:00’类型，转换为时间戳再加上result['time']才是表中的start_time类型
            time = result_match['starttime']
            strs = time.split(':')
            start_time = int(strs[0]) * 3600 + int(strs[1]) * 60 + date_time
            start_time = str(start_time)

            # 拿到网站的赛事id,拼凑出详情的url
            match_details_url = match_detail_url.format(source_matchid)
            # print('拿到的对局url:', source_matchid, match_details_url)

            # 用xpath提取出对局页面的小局id存到列表中
            response = requests.get(match_details_url, headers)
            response = response.text
            html = etree.HTML(response)

            match_detail_ids = html.xpath('//*[@id="info"]/div[2]/div[3]/ul/li/@match')
            # print('得到的小局id:', match_detail_ids)

            # 模拟点击拿该场赛程所有小场比赛时长字典
            duration_dict = parse_duration(match_details_url, match_detail_ids)
            index_num = len(match_detail_ids)
            for match_detail_id in match_detail_ids:
                # 拿到每场小局id去redis查找赛程记录
                result_check = redis_check(redis, game_name, db, source_from, league_name, match_detail_id,
                                           home_team, guest_name, start_time)
                # print('redis返回的赛程信息：', result_check)
                match_id = result_check[0]

                # 赛程在赛程表中找到记录
                if match_id:
                    team_a_name = result_check[4]
                    team_b_name = result_check[5]
                    sql_check = 'select team_a_name, team_a_id, team_b_name, team_b_id from game_python_match ' \
                                'where id = {}'.format(match_id)
                    result_team = db.select_message(sql_check)
                    team_a_realname = result_team[0]
                    team_b_realname = result_team[2]
                    team_a_id = result_team[1]
                    team_b_id = result_team[3]

                    # 判断网站的主客队与赛程表中主客队是否一致
                    judge_reversal = False
                    # 如果wanplus主客队校正后与表中a,b队相反，以表为准，此时wanplus的b队是主队(一般不会)
                    if team_a_name == team_b_realname and team_b_name == team_a_realname:
                        judge_reversal = True

                    #拿到小局id拼凑出更细致的详情页面
                    match_more_details_url = match_more_detail_url.format(match_detail_id)
                    # print('小局的对局详情url:', match_more_details_url)


                    # 开始分析小局详情页
                    parse_detail_wanplus(match_more_details_url, source_from, types, team_a_id, team_b_id, league_name, match_id, status,
                                         index_num, duration_dict, judge_reversal, match_detail_id)
                    # 小局的长次数用index_num
                    index_num -= 1
    # except Exception as e:
    #     match_detail_wanplus_log.error('数据抓取异常')
    #     match_detail_wanplus_log.error(e)


# 模拟点击获取比赛时长
def parse_duration(match_details_url, match_detail_ids):
    # 字典键值对形式: 小局第几场: 小局比赛时长
    duration_dict = {}
    driver.get(match_details_url)
    # 小场个数,判断需要点击几次(最后一次比赛时长不需要点击,因为默认展示的是最后一场的)
    count = len(match_detail_ids)
    for i in range(count):
        # # 先给字典的值默认为0
        duration_dict[count-i] = 0
        if i !=0:
            # 第一个比赛时长(最后一场)不需要点击
            driver.find_element_by_xpath('//*[@id="info"]/div[2]/div[3]/ul/li[{}]'.format(i+1)).click()
        time.sleep(0.5)
        # 拿到时长格式为'26:53'
        duration = driver.find_element_by_xpath('//*[@id="info"]/div[2]/div[3]/div[2]/ul/li[1]/div/div[2]').text
        duration = duration[-5::]
        result_time = duration.split(':')
        duration = int(result_time[0]) * 60 + int(result_time[1])
        duration_dict[count-i] = duration

    # print('拿到比赛时长字典为:', duration_dict)
    return duration_dict


def parse_detail_wanplus(match_more_details_url, source, types, team_a_id, team_b_id, league_name, match_id, status, index_num,
                         duration_dict, judge_reversal, match_detail_id):
    response = requests.get(match_more_details_url, headers_wanplus)
    response = response.text
    html = etree.HTML(response)

    # 团队推塔,团队经济
    team_a_kill_count = html.xpath('//*[@id="data"]/ul[1]/li[3]/div[1]/span[1]/text()')[0]
    team_b_kill_count = html.xpath('//*[@id="data"]/ul[1]/li[3]/div[1]/span[3]/text()')[0]
    team_a_tower_count = html.xpath('//*[@id="data"]/ul[1]/li[4]/div[1]/span[1]/text()')[0]
    team_b_tower_count = html.xpath('//*[@id="data"]/ul[1]/li[4]/div[1]/span[3]/text()')[0]
    team_a_money = html.xpath('//*[@id="data"]/ul[1]/li[2]/div[1]/span[1]/text()')[0]
    team_b_money = html.xpath('//*[@id="data"]/ul[1]/li[2]/div[1]/span[3]/text()')[0]
    win_left = html.xpath('//*[@id="data"]/ul[1]/li[1]/div/a[1]/span/span/text()')

    # 比赛时长
    # print('拿到的比赛时长和索引:', duration_dict, index_num, type(duration_dict), type(index_num))
    duration = duration_dict[index_num]


    # 选手死亡,,,,,
    # xpath拿到左右队伍的数据,默认左边为主队,右边为客队,但要根据judge_reversal判断

    left_death_assist_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[1]/span[1]/text()")
    right_death_assist_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[1]/span[3]/text()")
    left_damage_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[3]/span[1]/text()")
    right_damage_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[3]/span[3]/text()")
    left_damage_taken_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[4]/span[1]/text()")
    right_damage_taken_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[4]/span[3]/text()")
    left_money_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[2]/span[1]/text()")
    right_money_count = html.xpath("//div[@class='match_bans']/div[2]/ul/li[2]/span[3]/text()")

    # 死亡数和助攻数得到值列表:['3/3/6', '7/3/3', '3/2/4', '0/4/10', '0/4/10'] ,需要计算得到总的死亡数和助攻数
    # 记录每个选手的 击杀/阵亡/助攻到player_left字典
    # 格式为: position : [kill_count, death_count, assist_count, kda, damage_count, damage_taken_count, money_count]
    team_a_death_count = 0
    team_a_assist_count = 0
    count_left = 1

    # 根据列表索引可以判断选手的位置信息,因为在页面上是固定的
    # 将选手的字段数据填充到选手字典中
    # 格式为: position : [kill_count, death_count, assist_count, kda, money_count, damage_count, damage_taken_count]
    player_left = {
        1: [], 2: [], 3: [], 4: [], 5: []
    }
    player_right = {
        1: [], 2: [], 3: [], 4: [], 5: []
    }

    for kill_death_assist in left_death_assist_count:
        message = kill_death_assist.split('/')
        #计算左边团队死亡和助攻总数
        kda = round((int(message[0]) + int(message[2])) / (int(message[1]) + 1), 1)
        team_a_death_count += int(message[1])
        team_a_assist_count += int(message[2])
        # 记录左边每个选手的 击杀 死亡 助攻
        player_left[count_left].extend(message)
        player_left[count_left].append(kda)
        count_left += 1


    # 死亡数和助攻数得到值列表:['3/3/6', '7/3/3', '3/2/4', '0/4/10', '0/4/10'] ,需要计算得到总的死亡数和助攻数
    # 记录每个选手的 击杀/阵亡/助攻到player_right字典
    # 格式为: position : [kill_count, death_count, assist_count, kda, damage_count, damage_taken_count, money_count]
    team_b_death_count = 0
    team_b_assist_count = 0
    count_right = 1
    for kill_death_assist in right_death_assist_count:
        message = kill_death_assist.split('/')
        # print(message, type(message[0]))
        kda = round((int(message[0]) + int(message[2]))/(int(message[1])+1), 1)
        # 计算右边团队死亡和助攻总数
        team_b_death_count += int(message[1])
        team_b_assist_count += int(message[2])
        # 记录左边每个选手的 击杀 死亡 助攻
        player_right[count_right].extend(message)
        player_right[count_right].append(kda)
        count_right += 1


    # 左边添加money_count
    count_left = 1
    for money in left_money_count:
        player_left[count_left].append(money)
        count_left += 1

    # 右边添加money_count
    count_right = 1
    for money in right_money_count:
        player_right[count_right].append(money)
        count_right += 1

    # 左边添加damage_count
    count_left = 1
    for damage in left_damage_count:
        player_left[count_left].append(damage)
        count_left += 1

    # 右边添加damage_count
    count_right = 1
    for damage in right_damage_count:
        player_right[count_right].append(damage)
        count_right += 1

    # 左边添加damage_taken_count
    count_left = 1
    for damage_taken in left_damage_taken_count:
        player_left[count_left].append(damage_taken)
        count_left += 1

    # 右边添加damage_taken_count
    count_right = 1
    for damage_taken in right_damage_taken_count:
        player_right[count_right].append(damage_taken)
        count_right += 1

    # print('左边的死亡数和助攻数:', team_a_death_count, team_a_assist_count, player_left)
    # print('右边的死亡数和助攻数:', team_b_death_count, team_b_assist_count, player_right)

    # match_id, duration, index_num, status, types, team_a_kill_count, team_b_kill_count, team_a_death_count,
    # team_b_death_count, team_a_assist_count, team_b_assist_count, team_a_tower_count, team_b_tower_count,
    # win_team, team_a_money, team_b_money, match_detail_id, source
    # 根据judge_reversal判断左右数据需不需要反转(页面与赛程表中主客队相反,需要以赛程表)
    # print(judge_reversal, win_left)
    if judge_reversal:
        # wanplus的主客队与赛程表中相反,以赛程表的主客队为准(一般不会出现)
        win_team = 'B' if win_left == ['胜'] else 'A'
        team_a_kill_count, team_b_kill_count = team_b_kill_count, team_a_kill_count
        team_a_death_count, team_b_death_count = team_b_death_count, team_a_death_count
        team_a_assist_count, team_b_assist_count = team_b_assist_count, team_a_assist_count
        team_a_tower_count, team_b_tower_count = team_b_tower_count, team_a_tower_count
        team_a_money, team_b_money = team_b_money, team_a_money
    else:
        win_team = 'A' if win_left == ['胜'] else 'B'

    # print('左右位置的数据集合', player_left, player_right)
    # 选手对局记录
    messages = html.xpath("//div[@class='match_bans']")
    # 每组message有两个对位选手
    insert_count = 1
    for message in messages:
        # 左侧选手
        player_left_name = message.xpath('div[1]/div[1]/div[2]/p/a/strong/text()')[0]
        player_left_id = redis_check_playerID(player_left_name, source, redis, types, league_name, db)
        left_playerId_heroId = message.xpath('div[1]/div[1]/div[2]/p/a/@href')
        source_left_playerId = left_playerId_heroId[0].split('/')[-1]
        player_left_avater = player_avater.format(source_left_playerId)
        source_left_heroname = message.xpath('div[1]/div[1]/div[2]/p[2]/a/text()')[0]
        source_left_heroId = left_playerId_heroId[1].split('/')[-1]
        hero_left_avater = hero_avater.format(source_left_heroId)
        hero_left_id = redis_check_heroID(source_left_heroname, source, redis, types, league_name, db)
        # print('英雄和英雄返回的id:', source_left_heroname, hero_left_id)
        # 击杀/死亡/助攻 在player_left(player_left)字典的值列表[击杀, 死亡, 助攻]
        # position: [kill_count, death_count, assist_count, kda, damage_count, damage_taken_count, money_count]
        # print(player_left_id, hero_left_id)
        if player_left_id and hero_left_id:
            kill_left_count = player_left[insert_count][0]
            death_left_count = player_left[insert_count][1]
            assist_left_count = player_left[insert_count][2]
            kda = player_left[insert_count][3]
            money_count = player_left[insert_count][4]
            damage_count = player_left[insert_count][5]
            damage_taken_count = player_left[insert_count][6]


            # 装备和技能
            equip_left = message.xpath('div[1]/div[2]/a/img/@src')
            equip_left = str(equip_left)
            equip_left = equip_left.replace('\'', '\"')
            skill_left = message.xpath('div[3]/div[1]/div[1]/img/@src')
            skill_left = str(skill_left)
            skill_left = skill_left.replace('\'', '\"')
            # print('装备和技能:', equip_left, skill_left)
            # judge_reversal对于选手详情表的影响只有team_id
            team_id = team_b_id if judge_reversal else team_a_id
            # # 更新或插入选手对局详情表(有部分字段没有就不用写)
            sql_player = "INSERT INTO `game_player_battle_record` (match_id, player_id, player_name, player_avatar, " \
            "hero_id, hero_name, hero_avatar, kill_count, death_count, assist_count, damage_count, damage_taken_count, kda, " \
            "money_count, equip_ids, skill_ids, position, type, source_matchid, team_id, source_from) VALUES({0}, " \
            "{1}, '{2}', '{3}', {4}, '{5}', '{6}', {7}, {8}, {9}, {10}, {11}, {12}, {13}, '{14}', '{15}', {16}, {17}, " \
            "{18}, {19}, '{20}') " \
                         "ON DUPLICATE KEY UPDATE " \
            "match_id = {0}, player_id = {1}, player_name='{2}', player_avatar = '{3}', hero_id = {4}, hero_name = '{5}', " \
            "hero_avatar = '{6}', kill_count = {7}, death_count = {8}, assist_count = {9}, damage_count = {10}, " \
            "damage_taken_count = {11}, kda = {12}, money_count = {13}, equip_ids='{14}', skill_ids='{15}', " \
            "position = '{16}', type = '{17}', source_matchid={18}, team_id={19}, source_from='{20}';".format(
            match_id, player_left_id, player_left_name, player_left_avater, hero_left_id, source_left_heroname,
            hero_left_avater, kill_left_count, death_left_count, assist_left_count, damage_count, damage_taken_count,
            kda, money_count, equip_left, skill_left, insert_count, types, match_detail_id, team_id, source)
            # print('记录左边选手表：', sql_player)
            db.update_insert(sql_player)
            # print('记录左边选手表插入完成')


        # 右侧选手
        player_right_name = message.xpath('div[3]/div[1]/div[2]/p/a/strong/text()')[0]
        # print(1111, player_right_name)
        player_right_id = redis_check_playerID(player_right_name, source, redis, types, league_name, db)
        right_playerId_heroId = message.xpath('div[3]/div[1]/div[2]/p/a/@href')
        source_right_playerId = right_playerId_heroId[0].split('/')[-1]
        player_right_avater = player_avater.format(source_right_playerId)
        source_right_heroname = message.xpath('div[3]/div[1]/div[2]/p[2]/a/text()')[0]
        source_right_heroId = right_playerId_heroId[1].split('/')[-1]
        hero_right_avater = hero_avater.format(source_right_heroId)
        hero_right_id = redis_check_heroID(source_right_heroname, source, redis, types, league_name, db)
        # print('英雄和英雄返回的id:', source_right_heroname, hero_right_id)
        # 击杀/死亡/助攻 在player_left(player_left)字典的值列表[击杀, 死亡, 助攻]
        # position: [kill_count, death_count, assist_count, kda, damage_count, damage_taken_count, money_count]
        if player_right_id and hero_right_id:
            kill_right_count = player_right[insert_count][0]
            death_right_count = player_right[insert_count][1]
            assist_right_count = player_right[insert_count][2]
            kda = player_right[insert_count][3]
            money_count = player_right[insert_count][4]
            damage_count = player_right[insert_count][5]
            damage_taken_count = player_right[insert_count][6]


            # 装备和技能
            equip_right = message.xpath('div[3]/div[2]/a/img/@src')
            equip_right = str(equip_right)
            equip_right = equip_right.replace('\'', '\"')
            skill_right = message.xpath('div[1]/div[1]/div[1]/img/@src')
            skill_right = str(skill_right)
            skill_right = skill_right.replace('\'', '\"')

            # judge_reversal对于选手详情表的影响只有team_id
            team_id = team_a_id if judge_reversal else team_b_id
            # # 更新或插入选手对局详情表(有部分字段没有就不用写)
            sql_player = "INSERT INTO `game_player_battle_record` (match_id, player_id, player_name, player_avatar, " \
            "hero_id, hero_name, hero_avatar, kill_count, death_count, assist_count, damage_count, damage_taken_count, kda, " \
            "money_count, equip_ids, skill_ids, position, type, source_matchid, team_id, source_from) VALUES({0}, " \
            "{1}, '{2}', '{3}', {4}, '{5}', '{6}', {7}, {8}, {9}, {10}, {11}, {12}, {13}, '{14}', '{15}', {16}, {17}, " \
            "{18}, {19}, '{20}') " \
                "ON DUPLICATE KEY UPDATE " \
            "match_id = {0}, player_id = {1}, player_name='{2}', player_avatar ='{3}', hero_id = {4}, hero_name ='{5}', " \
            "hero_avatar = '{6}', kill_count = {7}, death_count = {8}, assist_count = {9}, damage_count = {10}, " \
            "damage_taken_count = {11}, kda = {12}, money_count = {13}, equip_ids='{14}', skill_ids='{15}',position = {16}, " \
            "type = {17}, source_matchid={18}, team_id={19}, source_from='{20}';".format(match_id, player_right_id,
            player_right_name, player_right_avater, hero_right_id, source_right_heroname, hero_right_avater,
            kill_right_count, death_right_count, assist_right_count, damage_count, damage_taken_count, kda,
            money_count, equip_right, skill_right,insert_count, types, match_detail_id, team_id, source)
            # print('记录右边选手表：', sql_player)
            db.update_insert(sql_player)
            # print('记录右边选手表插入完成')
        # 位置依次加一
        insert_count += 1

    # 更新或插入对局详情表(有部分字段没有就不用写)
    sql_battle_insert = "INSERT INTO `game_match_battle` (match_id, duration, index_num," \
    " status, type, team_a_kill_count, team_b_kill_count, team_a_death_count, team_b_death_count, team_a_assist_count, " \
    "team_b_assist_count, team_a_tower_count, team_b_tower_count, win_team, team_a_money, team_b_money, " \
    "source_matchid, source_from) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, '{13}', " \
    "{14}, {15}, {16}, '{17}') " \
               "ON DUPLICATE KEY UPDATE " \
    "match_id = {0}, duration = {1}, index_num={2}, status = {3}, type = {4}, team_a_kill_count = {5}, " \
    "team_b_kill_count = {6}, team_a_death_count = {7}, team_b_death_count = {8}, team_a_assist_count = {9}, " \
    "team_b_assist_count = {10}, team_a_tower_count = {11}, team_b_tower_count = {12}, win_team = '{13}', " \
    "team_a_money = {14}, team_b_money = {15}, source_matchid={16}, source_from='{17}';".format(
    match_id, duration, index_num, status, types, team_a_kill_count, team_b_kill_count, team_a_death_count,
    team_b_death_count, team_a_assist_count, team_b_assist_count, team_a_tower_count, team_b_tower_count,
    win_team, team_a_money, team_b_money, match_detail_id, source)
    # print('团队的sql:', sql_battle_insert)
    db.update_insert(sql_battle_insert)
    # print('团队sql执行完成')










# 上周的赛程
# print('开始抓上周赛程')
form_data = {
    '_gtk': 121196025,
    'game': 6,
    'time': last_weekstamp,
    'eids': ''
}
parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
# print('上周赛程已抓取')

# 本周的赛程 64806
# print('开始抓本周赛程')
form_data = {
    '_gtk': 121196025,
    'game': 6,
    'time': monday_stamp,
    'eids': ''
}
parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
# print('本周赛程已抓取')

# 关闭selenium驱动
driver.quit()
