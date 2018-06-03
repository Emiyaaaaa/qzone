# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:25
import os
from qzone_sql import GetQzoneToMysql
from deal_zdx_txt import DealTxtImg

max_page = 100

def get_qzone_html():

    print('当前网络状态：',end='')
    if os.system('ping www.baidu.com') == 0:
        print('畅通')
        GetQzoneToMysql().get_qzone(max_page)
    else:
        print('离线模式')


def deal_txt():
    pass


# get_qzone_html()