
## dev
db_setting = {
    'host': '127.0.0.1',
    'user': 'root',
    'password' : '0000',
    'db' : 'Game'
}


## product
#db_setting = {
#     'host': '116.62.47.187',
#     'user': 'ele_python',
#     'password' : 'ele_python',
#     'db' : 'ele_python'
# }

#   英雄联盟官网的url  headers---> headers_yxlmgw
# 正常情况下赛程页面是 url_finish_1：显示2条已完成  url_matching：进行中（status为‘-1’就是没有进行中的比赛） url_unfinish： 未开始

#  url_finish_2, url_finish_3 ：包含一周内已完成的比赛
#  url_unfinish_2, url_unfinish_3 ：包含一周内已完成的比赛

url_finish_1 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&' \
             'p10=&p6=2&p11=&p12=&page=1&pagesize=2&_='
url_finish_2 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=2&p11=6218&p12=&page=1&pagesize=8&_='
url_finish_3 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=2&p11=6210&p12=&page=1&pagesize=8&_='
url_finishs = [url_finish_1, url_finish_2, url_finish_3]

url_matching = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=9999&_='

url_unfinish_1 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=10&_='
url_unfinish_2 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=' \
                 '&p10=&p6=3&p11=&p12=6229&page=1&pagesize=8&_='
url_unfinish_3 = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=&p2=%C8%AB%B2%BF&p9=' \
                 '&p10=&p6=3&p11=&p12=6237&page=1&pagesize=8&_='
url_unfinishs = [url_unfinish_1, url_unfinish_2, url_unfinish_3]


headers_yxlmgw = {
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }






# 王者荣耀官网的url  headers
# 官网默认加载2页
url_wzrygw_1 = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage1.json'
url_wzrygw_2 = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage2.json'
url_wzrygw = [url_wzrygw_1, url_wzrygw_2]
headers_wzrygw = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

