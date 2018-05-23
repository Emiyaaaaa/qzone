# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:25
import os
from qzone.qzone_sql import GetQzoneToMysql

def main():
    print('当前网络状态：',end='')
    exit_code = os.system('ping www.baidu.com')
    if exit_code == 0:
        print('畅通')
        q = GetQzoneToMysql()
        q.get_qzone()
    else:
        print('离线模式')


main()