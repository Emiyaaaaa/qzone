# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:25
import os
from qzone_sql import GetQzoneToMysql
from deal_zdx_txt import DealTxtImg
from deal_sql import DealAll,DealSql

max_page = 100


def get_qzone_html():

    if os.system('ping www.baidu.com') == 0:
        GetQzoneToMysql().get_qzone(max_page)
    else:
        pass


def deal_txt():
    txt,img = DealSql().deal_html()
    txt_img_list = DealAll().main(txt, img)


get_qzone_html()