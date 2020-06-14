
# dev
db_setting = {
    'host': '127.0.0.1',
    'user': 'root',
    'password' : '0000',
    'db' : 'Game'
}

# product
# db_setting = {
#     'host': '127.0.0.1',
#     'user': 'root',
#     'password' : '0000',
#     'db' : 'Game'
# }


#   英雄联盟官网的url  headers---> url_finish：已完成    url_matching：进行中    url_unfinish：未进行 (后面加上时间戳)
url_finish = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=3&p2=%C8%AB%B2%BF&p9=&' \
             'p10=&p6=2&p11=&p12=&page=1&pagesize=2&_='
url_matching = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=2&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=9999&_='
url_unfinish = 'https://apps.game.qq.com/lol/match/apis/searchBMatchInfo_bak.php?p8=5&p1=134&p4=1&p2=%C8%AB%B2%BF&p9=&' \
               'p10=&p6=3&p11=&p12=&page=1&pagesize=10&_='

headers_yxlmgw = {
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }






# 王者荣耀官网的url  headers
url_wzrygw = 'https://itea-cdn.qq.com/file/ingame/smoba/allMatchpage1.json'
headers_wzrygw = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

