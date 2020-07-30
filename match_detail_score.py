# -*-coding:utf-8-*-
import json
import requests
from common_tool import post_response, get_log, get_weeks, get_response, redis_check
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
print(date_list)

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
        # print('需要拿的赛程日期:', date_list)
        print(len(results), type(results), results)
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
                    detail_list = detail_list['result']
                    for resultID in detail_list:
                        resultID = resultID['resultID']
                        detail_urls = detail_url.format(resultID, now_date_stamp)
                        print('详情url：', detail_urls)
                        detail_parse(detail_urls, source_matchid, types, game_name, league_name, headers)
    except Exception as e:
        match_detail_score_log.error(e)



def detail_parse(url, source_matchid, types, game_name, league_name, headers):
    result = get_response(url, headers)
    result = result['data']['result_list']
    # 先暂且把蓝方当主队，红方当客队请求后端拿到规范后的队名
    home_team = result['blue_name']
    guest_name = result['red_name']
    # redis中加入网站源标记
    source = 'SN网站'
    game_name = '英雄联盟'
    result = redis_check(redis, game_name, db, source, league_name, source_matchid, home_team, guest_name, matchTime)
    match_id = result[0] if result else None
    # 后端返回600且match_id不为空，说明对局详情在赛程表中匹配到赛程
    if result and match_id:









# 本周的比赛：form_data中的date参数为空
form_data['data'] = ''
parse(start_url, form_data, headers)
# print('----------------')
# 上周的比赛：form_data中的date参数为上周五的日期，例如：2020-07-26
form_data['data'] = last_friday_str
parse(start_url, form_data, headers)












