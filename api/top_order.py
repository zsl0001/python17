import pymysql
import re
import json

conn = pymysql.connect(host='122.51.209.32', port=3306, user='root', passwd='123456', db='acctop', charset='utf8')
# 使用cursor方法创建一个游标
cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)


def get_top_order_info(values):
    l = []
    sql = "select * from top_order where pacthCode = '{}'".format(values)
    cursor.execute(sql)  # 返回受影响的行数
    res = cursor.fetchall()  # 返回数据,返回的是tuple类型
    for item in res:
        b = re.findall(r'({.*?})', item['content'])
        b_dict = json.loads(b[0])
        l.append({'Bsart': b_dict['Bsart'], "Brgew": b_dict['Brgew'], 'Volum': b_dict['Volum'],'Zebeln':b_dict['Zebeln'],'creatime':item['creatime'],'oper':item['oper']})  # Volum 体积  Brgew 重量 Zebeln 主单编号
    cursor.close()
    conn.close()
    return l


# 2200184261
# b = get_top_order_info(2200184261)
# print(b)