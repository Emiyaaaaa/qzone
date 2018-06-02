# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:12

import pymysql
import re
from deal_all_txt import DealAll

maxinfo = 300 # 测试信息数量


class DealSql(object):

    def down_sql(self):
        connect = pymysql.connect(host='127.0.0.1',
                                  port=3306,
                                  user='root',
                                  password='1234',
                                  charset='utf8',
                                  )
        cursor = connect.cursor()
        cursor.execute('USE qzone')

        return cursor,connect

    def extract_html(self):

        cursor,connect = self.down_sql()

        cursor.execute('SELECT id FROM qzone_html')
        id_all = cursor.fetchall()
        if id_all == ():
            print('请检查网络状态！')
        else:
            for id in id_all[:maxinfo]:
                cursor.execute('SELECT html FROM qzone_html WHERE id=' + str(id[0]))
                html = cursor.fetchall()[0][0]
                if html == 'lhz':
                    continue
                cursor.execute('SELECT time FROM qzone_html WHERE id=' + str(id[0]))
                time = cursor.fetchall()[0][0]
                txt,img = self.deal_html(html)
                self.up_sql(txt,img)


    def deal_html(self,html):


        text_all_re = r'a href="http://rc.qzone.qq.com/qzonesoso/\?search=[\s\S]+?" target="_blank">#([\s\S]+?)#</a>([\s\S]+?)<'  # 小技巧：最开头去掉 <
        text_re = r'<a href="http://rc.qzone.qq.com/qzonesoso/\?search=%E6%89%BE%E5%AF%B9%E8%B1%A1&amp;entry=99&amp;businesstype=mood" target="_blank">#找对象#</a>([\s\S]+?)<'
        img_re = r'<a href="(http://b\d+.photo.store.qq.com/psb\?/.*?|http://m.qpic.cn/psb\?/.*?)"[\s\S]+?title="查看大图"'

        txt = re.findall(text_all_re,html)
        img = re.findall(img_re,html)
        img,txt = DealAll().deal_all(txt,img)

        return txt,img




    def up_sql(self,txt,img):
        pass


if __name__ == '__main__':
    DealSql().extract_html()