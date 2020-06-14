# -*-coding:utf-8-*-
import json
import requests
import urllib3
from common_tool import api_check, check_local, API_return_600, API_return_200
from import_data_to_mysql import con_db
from setting import url_wzrygw, headers_wzrygw


"""
王者荣耀官网爬虫
"""
def parse():
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url=url_wzrygw, headers=headers_wzrygw, verify = False)
    response = response.text
    response = json.loads(response)
    sources = response['matchList']
    print('抓取到的源数据：',len(response), response)
    game_name = '王者荣耀'
    type = 1
    for source in sources:
        league_sourcename = source['cate'] + source['match_name']
        # 每个模块分一个或多个比赛
        source_lists = source['match']
        for source_list in source_lists:
            # status: (0:未进行, 1：进行中, 2：已完成)
            status = source_list['status']
            team_a_sourcename = source_list['teama_name']
            team_b_sourcename = source_list['teamb_name']
            start_time = source_list['mtime']
            # 访问接口前先在表中用check_match字段匹配一下，有就不再访问接口（check_match字段就是四个源字段的字符串拼接）
            check_match = league_sourcename + team_a_sourcename + team_b_sourcename + start_time
            status_check = check_local(db, check_match)
            if status_check == None:
                # 请求检测接口
                result = api_check(game_name, league_sourcename, team_a_sourcename, team_b_sourcename)
                print('检测接口返回：', result)

                if result['code'] == 600:
                    insert_argument = {}
                    insert_argument['status'] = status
                    insert_argument['bo'] =
                    team_a_score = insert_argument['team_a_score']
                    team_b_score = insert_argument['team_b_score']
                    check_match = insert_argument['check_match']
                    win_team = insert_argument['win_team']
                   API_return_600(db, result, source_list, )





            print(game_name, status, league_name, team_a_name, team_b_name)
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


if __name__ == '__main__':
    # 创建mysql连接对象
    db = con_db()
    print('开始抓取比赛')
    parse()
    print('抓取比赛已完成')


