# -*-coding:utf-8-*-
from common_tool import post_response, get_log, redis_check, get_weeks
from import_data_to_redis import RedisCache_checkAPI
from import_data_to_mysql import con_db
from datetime import datetime
from setting import db_setting
from lxml import etree
import re
import requests

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

match_detail_wanplus_log = get_log('match_detail_wanplus')

redis = RedisCache_checkAPI()
db = con_db(db_setting['host'], db_setting['user'], db_setting['password'], db_setting['db'])

def parse_wanplus(url, data, db, headers):
    try:
        responses = post_response(url, data, headers)
        results = responses['data']['scheduleList']
        game_name = '王者荣耀'
        source_from = 'wanplus王者荣耀详情'  # 爬虫源网站
        types = 2
        for key_list, result in results.items():
            if key_list not in date_lists:
                continue
            date_time = result['time']
            results_match = result['list']
            # 有的字段是bool类型，过滤掉
            if type(results_match) == bool:
                continue
            for result_match in results_match:
                source_matchid = result_match['scheduleid']
                league_name = result_match['ename']
                home_team = result_match['oneseedname']
                guest_name = result_match['twoseedname']
                # 源数据中的start_time为‘17:00’类型，转换为时间戳再加上result['time']才是表中的start_time类型
                time = result_match['starttime']
                strs = time.split(':')
                start_time = int(strs[0]) * 3600 + int(strs[1]) * 60 + date_time
                start_time = str(start_time)
                result_check = redis_check(redis, game_name, db, source_from, league_name, source_matchid,
                                           home_team, guest_name, start_time)
                match_id = result_check[0]

                # 赛程在赛程表中找到记录
                if match_id:
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

                    # 判断网站的主客队与赛程表中主客队是否一致
                    judge_reversal = False
                    # 如果wanplus主客队校正后与表中a,b队相反，以表为准，此时wanplus的b队是主队(一般不会)
                    if team_a_name == team_b_realname and team_b_name == team_a_realname:
                        judge_reversal = True


                    # 拿到网站的赛事id,拼凑出详情的url
                    match_details_url = match_detail_url.format(source_matchid)
                    print('拿到的对局url:', source_matchid, match_details_url)

                    # 用xpath提取出对局页面的小局id存到列表中
                    response = requests.get(match_details_url, headers)
                    response = response.text
                    html = etree.HTML(response)

                    # 拿到时长格式为'26:53'
                    try:
                        duration = html.xpath('//*[@id="info"]/div[2]/div[3]/ul/li/@match')
                        duration = duration[-5::]
                        result_time = duration.split(':')
                        duration = int(result_time[0]) * 60 + int(result_time[1])
                    except TypeError:
                        match_detail_wanplus_log.error('时长异常')

                    match_detail_ids = html.xpath('//*[@id="info"]/div[2]/div[3]/ul/li/@match')
                    print('得到的小局id:', match_detail_ids)

                    for match_detail_id in match_detail_ids:
                        #拿到小局id拼凑出更细致的详情页面
                        match_more_details_url = match_more_detail_url.format(match_detail_id)
                        print('小局的对局详情url:', match_more_details_url)



    except Exception as e:
        match_detail_wanplus_log.error(e, exc_info=True)



# 上周的赛程
print('开始抓上周赛程')
form_data = {
    '_gtk': 121196025,
    'game': 6,
    'time': last_weekstamp,
    'eids': ''
}
parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
print('上周赛程已抓取')

# # 本周的赛程 64806
# print('开始抓本周赛程')
# form_data = {
#     '_gtk': 121196025,
#     'game': 6,
#     'time': monday_stamp,
#     'eids': ''
# }
# parse_wanplus(start_url_wanplus, form_data, db, headers_wanplus)
# print('本周赛程已抓取')
