
import json

import requests
import urllib3
import time
from API_check import api_check

# 王者荣耀赛事官网
url = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage1.json'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

requests.packages.urllib3.disable_warnings()
response = requests.get(url=url, headers=headers, verify = False)
results = response.text
results = json.loads(results)
sources = results['matchList']
print('抓取到的源数据：',results)

# 类型为王者荣耀
# 根据 game_name, league_name, team_a_name, team_b_name请求检测接口
game_name = '王者荣耀'

type = 1
for source in sources:
    league_name = source['cate'] + source['match_name']
    # 每个模块分一个或多个比赛
    source_lists = source['match']
    for source_list in source_lists:
        team_a_name = source_list['teama_name']
        team_b_name = source_list['teamb_name']
        print(game_name, league_name, team_a_name, team_b_name)
        # 请求检测接口
        result = api_check(game_name, league_name, team_a_name, team_b_name)
        print('检测接口返回：',result)

        # 拿到其余需要更新的字段
        import_data = {}
        import_data['type'] = type
        import_data['status'] = match_status
        import_data['bo'] = each_source['GameMode']
        import_data['team_a_score'] = each_source['ScoreA']
        import_data['team_b_score'] = each_source['ScoreB']
        if each_source['MatchWin'] == '1':
            import_data['win_team'] = 'A'
        elif each_source['MatchWin'] == '2':
            import_data['win_team'] = 'B'
        else:
            import_data['win_team'] = None





