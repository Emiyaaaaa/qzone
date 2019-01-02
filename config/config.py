#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/12/22 15:06
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXECUTABLE_PATH = "chromedriver.exe"
QQ = '486904330'
MAX_INFO = 50 # 数据库新增内容页数上限,设为 0 时默认上限为 1000
TEST_INFO = 205 # 测试信息数量


with open(os.path.join(BASE_DIR, 'config','QZone.pwd'), 'rb') as file:
    dict = pickle.load(file)

DATABASES = {
    'NAME': 'qzone',
    'USER': "root",
    'PASSWORD': dict['MySQLPassword'],
    'HOST': "60.205.207.236"
}