# -*-coding:utf-8-*-

import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')

import requests
from lxml import etree
from import_data_to_mysql import con_db
from setting import db_sport_setting
from common_tool import get_log


"""
竞彩网赔率爬虫
"""

db = con_db(db_sport_setting['host'], db_sport_setting['user'], db_sport_setting['password'], db_sport_setting['db'])

sport_bet_log = get_log('sport_bet')

bet_list = {
    'u-cir':2, 'u-dan':1, 'u-kong':0
}

headers_bet = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/84.0.4147.125 Safari/537.36'
}

start_url = 'https://info.sporttery.cn/football/match_list.php'

match_betdetail = 'https://www.lottery.gov.cn/football/match_hhad.jspx?mid='

response = requests.get(url=start_url, headers=headers_bet)
response = response.content.decode('gb2312')
html = etree.HTML(response)

# 联赛对应的国籍
type_contury = {
    '英超':'英国', '英冠': '英国', '英甲':'英国', '葡超':'葡萄牙', '意甲':'意大利', '西甲':'西班牙', '俄超':'俄罗斯',
    '日职':'日本', '日乙':'日本', '韩超':'韩国', '韩职': '韩国', '韩足总杯': '韩国', '德甲':'德国', '德乙':'德国','法甲':'法国',
    '瑞超':'瑞士', '挪超':'挪威', '澳超': '澳大利亚'
}

# 升降状态(暂定用颜色标签判定)
trend = {
    "['color:#1D9C00; font-weight:bold;']": -1,
    "['color:#DF3A00; font-weight:bold;']": 1,
    "[]":0
}

messages = html.xpath("//div[@class='match_list']/table//tr")
for message in messages:
    # s_id为赛程id，s_type为赛程类型
    s_id = message.xpath('td[3]/a/@href')
    s_type = message.xpath('td[2]/text()')
    # 如果赛程id和赛程类型不为空才继续抓取其余信息
    if s_id and s_type:
        s_id = s_id[0]
        s_id = s_id.split('m=')[1]
        s_type = s_type[0]
        company_name = '竞猜'
        try:
            country = type_contury[s_type] if s_type in type_contury else None
            match_beturl = match_betdetail + s_id
            # print(match_beturl)
            response_bet = requests.get(url=match_beturl, headers=headers_bet)
            response_bet = response_bet.text
            html_1 = etree.HTML(response_bet)
            # 胜平负赔率
            results_3010 = html_1.xpath('//table[@class="table2 yylMt20"]//tr')
            # print('胜平负总赔率：', match_beturl, results_3010)
            if len(results_3010) > 2:
                result_3010 = results_3010[2]
                counts = len(results_3010)
                for count in range(counts):
                    # 从第三个element对象开始
                    if count >=2:
                        result_3010 = results_3010[count]
                        update_num = str(result_3010.xpath('td[1]/text()')[0])
                        handicap_type = 1 if update_num == '1' else 2
                        odds_3 = str(result_3010.xpath('td[2]/text()')[0])
                        odds_3_trend = result_3010.xpath('td[2]/font/@style')
                        odds_3_trend = trend['{}'.format(odds_3_trend)]
                        odds_1 = str(result_3010.xpath('td[3]/text()')[0])
                        odds_1_trend = result_3010.xpath('td[3]/font/@style')
                        odds_1_trend = trend['{}'.format(odds_1_trend)]
                        odds_0 = str(result_3010.xpath('td[4]/text()')[0])
                        odds_0_trend = result_3010.xpath('td[4]/font/@style')
                        odds_0_trend = trend['{}'.format(odds_0_trend)]
                        # print('单个详情赔率:', match_beturl, odds_3, odds_3_trend, odds_1, odds_1_trend, odds_0, odds_0_trend)
                        sql_3010 = "INSERT INTO `jc_odds_3010` (jc_mid, company_name, country,update_num, handicap_type, odds_3, " \
                        "odds_3_trend, odds_1, odds_1_trend, odds_0, odds_0_trend) VALUES ({0}, '{1}', '{2}',{3}, {4}, {5}, {6}," \
                        " {7}, {8}, {9}, {10})" \
                                   "ON DUPLICATE KEY UPDATE " \
                        "company_name='{1}', country='{2}', update_num={3}, handicap_type={4}, odds_3={5}, odds_3_trend={6}, " \
                        "odds_1={7}, odds_1_trend={8}, odds_0={9}, odds_0_trend={10};".format(s_id, company_name, country,
                        update_num, handicap_type, odds_3, odds_3_trend, odds_1, odds_1_trend, odds_0, odds_0_trend)

                        # print('胜平负开始写入:', sql_3010)
                        db.update_insert(sql_3010)
                        # print('胜平负写入完成')

            # 让球胜平负赔率
            results_3010 = html_1.xpath('//table[@class="table3 yylMt20"]//tr')
            # print('让球胜平负总赔率：', match_beturl, results_3010)
            if len(results_3010) > 2:
                result_3010 = results_3010[2]
                counts = len(results_3010)
                for count in range(counts):
                    # 从第三个element对象开始
                    if count >=2:
                        result_3010 = results_3010[count]
                        update_num = str(result_3010.xpath('td[1]/text()')[0])
                        handicap_type = 1 if update_num == '1' else 2
                        rq_num = str(result_3010.xpath('td[2]/text()')[0])
                        odds_3 = str(result_3010.xpath('td[3]/text()')[0])
                        odds_3_trend = result_3010.xpath('td[3]/font/@style')
                        odds_3_trend = trend['{}'.format(odds_3_trend)]
                        odds_1 = str(result_3010.xpath('td[4]/text()')[0])
                        odds_1_trend = result_3010.xpath('td[4]/font/@style')
                        odds_1_trend = trend['{}'.format(odds_1_trend)]
                        odds_0 = str(result_3010.xpath('td[5]/text()')[0])
                        odds_0_trend = result_3010.xpath('td[5]/font/@style')
                        odds_0_trend = trend['{}'.format(odds_0_trend)]
                        # print('让球单个详情赔率:', match_beturl, handicap_type, rq_num, odds_3, odds_3_trend, odds_1, odds_1_trend, odds_0, odds_0_trend)

                        sql_3006 = "INSERT INTO `jc_odds_3006` (jc_mid, company_name, country, update_num, handicap_type, rq_num, odds_3, " \
                        "odds_3_trend, odds_1, odds_1_trend, odds_0, odds_0_trend) VALUES ({0}, '{1}', '{2}', {3}, {4}, {5}, {6}," \
                        " {7}, {8}, {9}, {10}, {11})" \
                                   "ON DUPLICATE KEY UPDATE " \
                        "company_name='{1}', country='{2}', update_num={3}, handicap_type={4}, rq_num= {5}, odds_3={6}, odds_3_trend={7}, " \
                        "odds_1={8}, odds_1_trend={9}, odds_0={10}, odds_0_trend={11};".format(s_id, company_name, country,
                        update_num, handicap_type, rq_num, odds_3, odds_3_trend, odds_1, odds_1_trend, odds_0, odds_0_trend)

                        # print('让球胜平负开始写入:', sql_3006)
                        db.update_insert(sql_3006)
                        # print('让球胜平负写入完成')

            # 总进球数赔率
            results_3010 = html_1.xpath('//table[@class="table5 yylMt20"]//tr')
            # print('让球胜平负总赔率：', match_beturl, results_3010)
            if len(results_3010) > 2:
                result_3010 = results_3010[2]
                counts = len(results_3010)
                for count in range(counts):
                    # 从第三个element对象开始
                    if count >= 2:
                        result_3010 = results_3010[count]
                        update_num = str(result_3010.xpath('td[1]/text()')[0])
                        handicap_type = 1 if update_num == '1' else 2
                        total_gold_0 = str(result_3010.xpath('td[2]/text()')[0])
                        total_gold_0_trend = result_3010.xpath('td[2]/font/@style')
                        total_gold_0_trend = trend['{}'.format(total_gold_0_trend)]
                        total_gold_1 = str(result_3010.xpath('td[3]/text()')[0])
                        total_gold_1_trend = result_3010.xpath('td[3]/font/@style')
                        total_gold_1_trend = trend['{}'.format(total_gold_1_trend)]
                        total_gold_2 = str(result_3010.xpath('td[4]/text()')[0])
                        total_gold_2_trend = result_3010.xpath('td[4]/font/@style')
                        total_gold_2_trend = trend['{}'.format(total_gold_2_trend)]
                        total_gold_3 = str(result_3010.xpath('td[5]/text()')[0])
                        total_gold_3_trend = result_3010.xpath('td[5]/font/@style')
                        total_gold_3_trend = trend['{}'.format(total_gold_3_trend)]
                        total_gold_4 = str(result_3010.xpath('td[6]/text()')[0])
                        total_gold_4_trend = result_3010.xpath('td[6]/font/@style')
                        total_gold_4_trend = trend['{}'.format(total_gold_4_trend)]
                        total_gold_5 = str(result_3010.xpath('td[7]/text()')[0])
                        total_gold_5_trend = result_3010.xpath('td[7]/font/@style')
                        total_gold_5_trend = trend['{}'.format(total_gold_5_trend)]
                        total_gold_6 = str(result_3010.xpath('td[8]/text()')[0])
                        total_gold_6_trend = result_3010.xpath('td[8]/font/@style')
                        total_gold_6_trend = trend['{}'.format(total_gold_6_trend)]
                        total_gold_7 = str(result_3010.xpath('td[9]/text()')[0])
                        total_gold_7_trend = result_3010.xpath('td[9]/font/@style')
                        total_gold_7_trend = trend['{}'.format(total_gold_7_trend)]
                        # print('让球单个详情赔率:', match_beturl, update_num, handicap_type, total_gold_0, total_gold_0_trend,
                        #       total_gold_1, total_gold_1_trend, total_gold_2, total_gold_2_trend, total_gold_3,
                        #       total_gold_3_trend, total_gold_4, total_gold_4_trend, total_gold_5, total_gold_5_trend,
                        #       total_gold_6, total_gold_6_trend, total_gold_7, total_gold_7_trend)

                        sql_3008 = "INSERT INTO `jc_odds_3008` (jc_mid, company_name, update_num, handicap_type, " \
                        "total_gold_0, total_gold_0_trend, total_gold_1, total_gold_1_trend, total_gold_2, total_gold_2_trend," \
                        " total_gold_3, total_gold_3_trend, total_gold_4, total_gold_4_trend, total_gold_5, total_gold_5_trend," \
                        " total_gold_6, total_gold_6_trend, total_gold_7, total_gold_7_trend) VALUES ({0}, '{1}', " \
                        "{2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19})" \
                                   "ON DUPLICATE KEY UPDATE " \
                        "company_name='{1}', update_num={2}, handicap_type={3}, total_gold_0= {4}, total_gold_0_trend={5}, total_gold_1={6}, " \
                        "total_gold_1_trend={7}, total_gold_2={8}, total_gold_2_trend={9}, total_gold_3={10}, " \
                        "total_gold_3_trend={11}, total_gold_4={12}, total_gold_4_trend={13}, total_gold_5={14}," \
                        " total_gold_5_trend={15}, total_gold_6={16}, total_gold_6_trend={17}, total_gold_7={18}, " \
                        "total_gold_7_trend={19};".format(s_id, company_name, update_num, handicap_type, total_gold_0,
                        total_gold_0_trend, total_gold_1, total_gold_1_trend, total_gold_2, total_gold_2_trend, total_gold_3,
                        total_gold_3_trend, total_gold_4, total_gold_4_trend, total_gold_5, total_gold_5_trend, total_gold_6,
                        total_gold_6_trend, total_gold_7, total_gold_7_trend)
                        # print('进球数赔率开始写入:', sql_3008)
                        db.update_insert(sql_3008)
                        # print('进球数赔率写入完成')
        except Exception as e:
            sport_bet_log.error('联赛种类异常')
            sport_bet_log.error(e, exc_info=True)
