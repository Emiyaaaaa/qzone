# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:25
import time
from selenium import webdriver
from extra_apps.qzone.qzone_sql import GetQzoneToMysql
from extra_apps.qzone.deal_sql import DealAll,DealSql
from extra_apps.qzone.config.config import *


def get_qzone_html():
    chromedriver = EXECUTABLE_PATH
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    while True:
        if os.system('ping www.baidu.com') == 0:
            GetQzoneToMysql().get_qzone(driver)
        else:
            time.sleep(20)
            continue
        time.sleep(1200)



def main():
    # get_qzone_html()
    txt,img = DealSql().deal_html()
    # print(txt,img)
    txt_img_list = DealAll().main(txt, img)
    # print(txt_img_list)

if __name__ == '__main__':
    get_qzone_html()