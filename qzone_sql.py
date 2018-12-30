# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/2 17:46

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
import pymysql
import os
from extra_apps.qzone.config.config import *

sql_new_time = []
time_list = []
auto_login = False

class GetQzoneToMysql(object):

    """
    1.get_qzone(self)
    2.get_time(self,text)
    3.up_mysql(self,text,time_,upload_time)
    4.new_time(self,time_,upload_time)
    """

    def connect_mysql(self):
        connect = pymysql.connect(
            host=DATABASES['HOST'],
            port=3306,
            user=DATABASES['USER'],
            password=DATABASES['PASSWORD'],
            charset='utf8mb4',
        )
        cursor = connect.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS qzone CHARACTER SET utf8mb4')
        cursor.execute('USE qzone')
        cursor.execute('CREATE TABLE IF NOT EXISTS qzone_html(html LONGTEXT,time VARCHAR(50),upload_time VARCHAR(50), text TEXT,id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, is_turned SMALLINT default 0)')

        # 为数据表设一个初始值
        cursor.execute('SELECT id FROM qzone_html')
        id_all = cursor.fetchall()
        if id_all == ():
            sql = 'INSERT INTO qzone_html (html,time,upload_time,is_turned) VALUES (%s,%s,%s,%s)'
            cursor.execute(sql, ('lhz', '1970年1月1日 08:00','1970年1月1日 08:00',0))
            connect.commit()
        return cursor,connect

    def up_mysql(self,text,time_,upload_time):

        cursor,connect = self.connect_mysql()


        cursor.execute('SELECT id FROM qzone_html')
        id_all = cursor.fetchall()
        finally_id = id_all[len(id_all) - 1][0]
        sql = 'SELECT upload_time FROM qzone_html WHERE id=' + str(finally_id)
        cursor.execute(sql)
        sql_new_time.append(cursor.fetchall()[0])


        timeArray = time.strptime(time_, "%Y年%m月%d日 %H:%M")
        time__ = time.mktime(timeArray)
        sql_new_time_ = time.mktime(time.strptime(sql_new_time[0][0], "%Y年%m月%d日 %H:%M"))
        new_time = self.new_time(time__, sql_new_time[0][0])
        if new_time == time__ and new_time != sql_new_time_:
            sql = 'INSERT INTO qzone_html (html,time,upload_time,is_turned) VALUES (%s,%s,%s,%s)'
            cursor.execute(sql, (text, time_,upload_time,0))
            connect.commit()
            return 'ok'
        else:
            return 'exit'
        connect.close()


    def get_qzone(self, max_info=MAX_INFO):
        if 'driver' not in locals():
            chromedriver = EXECUTABLE_PATH
            os.environ["webdriver.chrome.driver"] = chromedriver
            driver = webdriver.Chrome(chromedriver)
        driver.get('http://user.qzone.qq.com/{}/311'.format(QQ))
        time.sleep(6)
        try:
            driver.find_element_by_id('login_div')
            a = True
        except:
            a = False
        if a == True:
            if auto_login == True:
                with open(os.path.join(BASE_DIR, 'config', 'QZone.pwd'), 'rb') as file:
                    dict = pickle.load(file)
                QQPassword = dict['QQPassword']
                driver.switch_to.frame('login_frame')
                driver.find_element_by_id('switcher_plogin').click()
                driver.find_element_by_id('u').clear()#选择用户名框
                driver.find_element_by_id('u').send_keys('2914034404')
                driver.find_element_by_id('p').clear()
                driver.find_element_by_id('p').send_keys(QQPassword)
                driver.find_element_by_id('login_button').click()
                time.sleep(4)
                driver.implicitly_wait(4)
            else:
                time.sleep(20)
                #手动扫码
        try:
            driver.find_element_by_id('QM_OwnerInfo_Icon')
            b = True
        except:
            b = False
        if b == True:
            driver.switch_to.frame('app_canvas_frame')

            if max_info == 0:
                max_info = 1000
            for i in range(max_info):
                info = self.get_time(driver.page_source)

                if info == 'exit':
                    break
                else:
                    #nextpage
                    try:
                        driver.find_element_by_id(self.get_next_page(driver.page_source)).click()
                        time.sleep(3)
                    except BaseException:
                        time.sleep(3)
                        driver.find_element_by_id(self.get_next_page(driver.page_source)).click()
                        time.sleep(3)
                        continue

        # driver.close()
        # driver.quit()

    def get_next_page(self,txt):
        reg = r'<a href="javascript:void[\s\S]+?;"[\s\S]+?" title="下一页" id="([\s\S]+?)" class="c_tx">'
        next_page = re.findall(reg,txt)[0]
        print(next_page)
        return next_page

    def get_time(self,text):

        soup = BeautifulSoup(text, "lxml")
        li = soup.find_all('li', attrs={'class': 'feed', 'data-uin': '486904330'})
        time_re = r'<a class="c_tx c_tx3 goDetail"[\s\S]+?title="([\s\S]+?)"'
        text_re = r'<a href="http://rc.qzone.qq.com/qzonesoso/\?search=%E6%89%BE%E5%AF%B9%E8%B1%A1&amp;entry=99&amp;businesstype=mood" target="_blank">[\s\S]+?找对象#</a>([\s\S]+?)<(/pre|a)'

        info = ''
        for i in range(len(li)):
            if re.findall(text_re,str(li[i])) != []:
                time_ = re.findall(time_re, str(li[i]))
                if time_ != []:
                    time_list.append(time_)
                    upload_time = time_list[0]
                    try:
                        info = self.up_mysql(str(li[i]),time_[0],upload_time)
                        if info == 'ok':
                            print('succeed1')
                            time.sleep(1)
                    except BaseException as e:
                        print('failed')
                        print(e)
                        time.sleep(1)
                        continue

                    if info == 'exit':
                        break
                else:
                    print('time error!')
                    break

        return info

    def new_time(self,time_,upload_time):

        timeArray = time.strptime(upload_time, "%Y年%m月%d日 %H:%M")
        upload_time_ = time.mktime(timeArray)
        new_time = max(int(time_),int(upload_time_))

        return new_time


if __name__ == '__main__':

    GetQzoneToMysql().get_qzone()
