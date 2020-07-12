# -*-coding:utf-8-*-
import json
from datetime import datetime
import requests
import time
from lxml import etree
from import_data_to_mysql import con_db

"""
竞彩网赛程爬虫
"""

db = con_db()

bet_list = {
    'u-cir':2, 'u-dan':1, 'u-kong':0
}

headers_sport = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/83.0.4103.116 Safari/537.36'
}

start_url = 'https://info.sporttery.cn/football/match_list.php'


def parse():
    response = requests.get(url=start_url, headers=headers_sport)
    response = response.content.decode('gb2312')
    html = etree.HTML(response)

    messages = html.xpath("//div[@class='match_list']/table//tr")
    # print(messages)
    for message in messages:
        s_id = message.xpath('td[3]/a/@href')
        # 如果赛程id不为空才继续抓取其余信息
        if s_id:
            s_id = s_id[0]
            s_id = int(s_id.split('m=')[1])
            s_name = message.xpath('td[1]/text()')[0]
            l_name = message.xpath('td[2]/text()')[0]
            home_team = message.xpath('td[3]/a/span[1]/text()')[0]
            visitor_team = message.xpath('td[3]/a/span[3]/text()')[0]
            # 网站的时间没有精确到s，加上':00'后转化为dateime类型
            start_time_str = message.xpath('td[4]/text()')[0] + ':00'
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:00')
            spf_str = message.xpath('td[7]/a/div/@class')
            spf = bet_list[spf_str[0]] if spf_str else 0
            rqspf_str = message.xpath('td[8]/a/div/@class')
            rqspf = bet_list[rqspf_str[0]] if spf_str else 0
            bf_str = message.xpath('td[9]/a/div/@class')
            bf = bet_list[bf_str[0]] if spf_str else 0
            zjqs_str = message.xpath('td[10]/a/div/@class')
            zjqs = bet_list[zjqs_str[0]] if spf_str else 0
            bqc_str = message.xpath('td[11]/a/div/@class')
            bqc = bet_list[bqc_str[0]] if spf_str else 0
            status2 = message.xpath('td[6]/text()')[0]
            status2 = status2.strip()
            # print(s_id, s_name, l_name, home_team, visitor_team, start_time, spf, rqspf, bf, zjqs, bqc, status2)

            # 写入体育赛程表
            source_from = '竞彩网'
            sql_matchlist = "INSERT INTO `sporttery_zu` (s_id, s_name, l_name, home_team, visitor_team, start_time, spf, rqspf, bf," \
                  " zjqs, bqc, status2, source_from) VALUES({0}, '{1}', '{2}', '{3}', '{4}', '{5}', {6}, {7}, {8}, {9}, {10}, '{11}', '{12}')  " \
                  "ON DUPLICATE KEY UPDATE  " \
                  "s_name='{1}', l_name='{2}', home_team='{3}', visitor_team='{4}', start_time='{5}', spf={6}, rqspf={7}, bf={8}," \
                  " zjqs={9}, bqc={10}, status2='{11}', source_from='{12}';".format(s_id, s_name, l_name, home_team, visitor_team, start_time,
                                                               spf, rqspf, bf, zjqs, bqc, status2, source_from)
            # print('开始写入:', sql_matchlist)
            db.update_insert(sql_matchlist)
            # print('写入完成')

parse()