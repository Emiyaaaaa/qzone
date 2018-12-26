#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/9/29 12:22

import pickle

dict = {}
path = 'QZone.pwd'

with open(path, 'wb') as file:
    pickle.dump(dict,file)

with open(path, 'rb') as file:
    dict = pickle.load(file)

