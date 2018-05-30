# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/30 17:14

import time

# 用来更方便的写日志而已

filename = 'diary.txt'
txt = []
for i in range(10):
    txt_line = input()
    if txt_line == '':
        break
    txt.append(txt_line)


with open(filename,'a',encoding="utf-8") as fileobject:
    fileobject.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for txt in txt:
        fileobject.write('\n\t' + txt)
    fileobject.write('\n\n')
