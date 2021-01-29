import requests
from bs4 import BeautifulSoup
import pymysql
import time,datetime


class Administrative(object):
    def __init__(self):
        self.db = pymysql.connect("192.168.1.168", "root", "Nr123...", "wly", charset="utf8mb4")
        self.main()
        self.db.close()

    def main(self):
        base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/'
        trs = self.get_response(base_url, 'provincetr')
        for tr in trs:  # 循环每一行
            datas = []
            for td in tr:  # 循环每个省
                if td.a:
                    province_name = td.a.get_text()
                    province_url = base_url + td.a.get('href')
                    print(province_name)
                    data2 = [province_name, '0', '1', '0', datetime.datetime.now(),td.a.get('href').split('.')[0] + '0000']
                    if data2 not in datas:
                        datas.append(data2)
                    trs = self.get_response(province_url, None)
                    if trs:
                        for tr in trs[1:]:  # 循环每个市
                            city_code = tr.find_all('td')[0].string
                            city_name = tr.find_all('td')[1].string
                            city_url = base_url + tr.find_all('td')[1].a.get('href')
                            data3 = [city_name, td.a.get('href').split('.')[0] + '0000', '2', '0', datetime.datetime.now(),str(city_code)[:6]]
                            print(city_name, city_url)
                            datas.append(data3)
                            trs = self.get_response(city_url, None)
                            for tr in trs[1:]:  # 循环每个区
                                county_code = tr.find_all('td')[0].string
                                county_name = tr.find_all('td')[1].string
                                data = [str(county_name).encode('utf-8').decode('utf-8'), str(city_code)[:6], '3', '0',
                                        datetime.datetime.now(),str(county_code)[:6]]
                                print(data)
                                datas.append(data)
            sql = "insert into TMS_BasicArea_2020 (Area_Name,Area_ParentID,Area_NodeType,Area_Invalid,Area_InsertTime,Area_ID) values (%s,%s,%s,%s,%s,%s)"
            self.connect_mysql(sql, datas)

    def get_response(self, url, attr):
        count = 0
        while 1:
            count = count + 1
            print(count)
            response = requests.get(url)
            print(response.status_code)
            if response.status_code == 200:
                response.encoding = 'gb2312'  # 编码转换
                soup = BeautifulSoup(response.text, 'lxml')
                table = soup.find_all('tbody')[1].tbody.tbody.table
                if attr:
                    trs = table.find_all('tr', attrs={'class': attr})
                else:
                    trs = table.find_all('tr')
                return trs

    def connect_mysql(self, sql, data):
        cursor = self.db.cursor()
        try:
            result = None
            if data:
                if isinstance(data[0], list):
                    cursor.executemany(sql, data)
                else:
                    cursor.execute(sql, data)
            else:
                cursor.execute(sql)
                result = cursor.fetchall()
        except Exception as e:
            print(e)
            self.db.rollback();
        finally:
            cursor.close()
            self.db.commit();  # 提交操作
            return result


if __name__ == '__main__':
    Administrative()
