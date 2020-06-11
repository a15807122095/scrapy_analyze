
import requests
import json
#  访问后端接口验证是否需要添加记录或是更新记录
# payload = {
#             'game_name': result_game_name,
#             'league_name':result_tournament_name,
#             'team_a_name':result_team_A,
#             'team_b_name':result_team_B,
#            }

def api_check(payload):
        # 请求接口拿到数据
        url_check = 'http://dev.saishikong.com/data/backstage-api/python-search'
        final_response = requests.post(url=url_check, json=payload)
        result = json.loads(final_response.text)
        return result['result']

# 返回格式： {
#           "code":600,"msg":"success","result":
#                       {"league_id":"268063888",
#                       "league_name":"2020 LPL夏季赛",
#                       "team_a_id":"2663508672642",
#                       "team_a_name":"Snake WuDu",
#                       "team_b_id":"74",
#                       "team_b_name":"JDG电子竞技俱乐部"}
#                       }