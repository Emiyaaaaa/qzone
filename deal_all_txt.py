# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/31 19:25

import os
from deal_zdx_txt import DealTxtImg

class DealAll():

    def list_flatten(self, l, a=None):
        # 将多维数组转化为一维数组
        a = list(a) if isinstance(a, (list, tuple)) else []
        for i in l:
            if isinstance(i, (list, tuple)):
                a = DealAll().list_flatten(i, a)
            else:
                a.append(i)
        return a

    def remove_duplication(self,list):
        # 有序去重
        list_new = []
        for i in list:
            if i not in list_new:
                list_new.append(i)
        list = list_new

        return list


    def deal_all(self, txt, img):
        tag_list = []
        txt_list = []
        img_list = []  # 元素并不是数字，而是图片url
        txt_else_list = []
        img_else_list = []

        for txt_ in txt:
            tag_list.append(txt_[0])
            txt_list.append(txt_[1])

        for img_ in img:
            img_list.append(img_)

        img_all = len(img)
        tag_all = len(txt)
        zdx_num = tag_list.index('找对象')
        zdx_txt = txt[zdx_num][1]

        # 此处开始分析
        text, img_num = DealTxtImg().main(zdx_txt)
        if tag_all != 1 and self.list_flatten(img_num) == []:
            # 多个tag，且zdx tag下全为空(空已转化为'zdx')
            for txt_ in txt_list:
                txt_else, img_num_else = DealTxtImg().main(txt_)
                txt_else_list.append(txt_else)
                img_else_list.append(img_num_else)

            for i in range(len(img_else_list[zdx_num])):
                # 为zdx_txt 添加特有标志
                if img_else_list[zdx_num][i] == []:
                    img_else_list[zdx_num][i] = ['zdx']

            if tag_all == img_all:
                img = [zdx_num]

            elif tag_all > img_all:
                img = ['unknow']

            else:
                img_temp_list = self.list_flatten(img_else_list)
                if self.remove_duplication(img_temp_list) == ['zdx']:
                    img = []
            print(txt)
            print(txt_else_list, img_else_list)
            print(' img:'+str(img_all))

        return txt,img # 注意修改


if __name__ == '__main__':
    os.system(os.path.join(os.path.abspath('.'), 'deal_sql.py'))