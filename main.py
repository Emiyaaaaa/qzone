# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:25
import os
import time
from extra_apps.qzone.qzone_sql import GetQzoneToMysql
from extra_apps.qzone.deal_sql import DealAll,DealSql

max_page = 100

def get_qzone_html():
    while True:
        if os.system('ping www.baidu.com') == 0:
            GetQzoneToMysql().get_qzone(max_page)
        else:
            time.sleep(20)
            continue
        time.sleep(3600)



def main():
    # get_qzone_html()
    txt,img = DealSql().deal_html()
    # print(txt,img)
    txt_img_list = DealAll().main(txt, img)
    # print(txt_img_list)

if __name__ == '__main__':
    get_qzone_html()