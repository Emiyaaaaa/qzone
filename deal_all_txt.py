# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/31 19:25

import os
import re
import copy
from deal_zdx_txt import DealTxtImg

class DealAll():

    def list_flatten(self, l, a=None):
        # 将多维数组转化为一维数组
        a = list(a) if isinstance(a, (list, tuple)) else []
        for i in l:
            if isinstance(i, (list, tuple)):
                a = self.list_flatten(i, a)
            else:
                a.append(i)
        return a

    def list_flatten_add_space(self, l):
        # 将多维数组转化为一维数组,并将空元素转化为空格
        l_copy = copy.deepcopy(l)
        for i in range(len(l_copy)):
            for j in range(len(l_copy[i])):
                l_copy
                if l_copy[i][j] == []:
                    l_copy[i][j] = [' ']
        l_copy = self.list_flatten(l_copy)
        return l_copy

    def list_num(self, l, num = 0):
        # 计算三维数组元素个数(包括空元素)
        for i in range(len(l)):
            for j in range(len(l[i])):
                num = num + len(l[i][j])
                if l[i][j] == []:
                    num = num+1
        return num


    def remove_duplication(self,list):
        # 有序去重
        list_new = []
        for i in list:
            if i not in list_new:
                list_new.append(i)
        list = list_new

        return list

    def txt_num(self,txt):
        # 判断文本约使用了几张图片
        txt = DealTxtImg().del_else(txt)
        if re.findall(u'[和|两|与|跟]',txt):
            try:
                if txt[txt.index(re.findall(u'[和|两|与|跟]', txt)[0]) + 1] == u'墙':
                    return 1
                else:
                    return 2
            except:
                return 2
        elif re.findall(u'三',txt):
            return 3
        elif re.findall(u'好多',txt):
            return 3
        elif re.findall(u'四', txt):
            return 4
        else:
            return 1

    def list_finder(self, ele, list):
        # 查找所有目标元素的索引
        return [a for a in range(len(list)) if list[a] == ele]

    def deal_all(self, txt, img):
        tag_list = []
        txt_list = []
        img_list = []  # 元素并不是数字，而是图片url
        txt_all_list = []
        img_all_list = []
        img_num_list = []
        num_list = []

        for txt_ in txt:
            tag_list.append(txt_[0])
            txt_list.append(txt_[1])

        for img_ in img:
            img_list.append(img_)

        img_num = len(img)
        tag_num = len(txt)
        zdx_num = tag_list.index('找对象')
        zdx_txt = txt[zdx_num][1]

        for txt_ in txt_list:
            txt_all, img_num_all = DealTxtImg().main(txt_)
            txt_all_list.append(txt_all)
            img_all_list.append(img_num_all)

        # 此处开始分析
        txt_zdx, img_zdx = DealTxtImg().main(zdx_txt)

        if self.list_flatten_add_space(img_zdx) != [] and ' ' not in self.list_flatten_add_space(img_zdx):
            # 1.直接可以知道图号的
            img_num_list = self.list_flatten(img_zdx)


        elif tag_num == 1:
            # 2.没有其他tag的
            img_num_list = [1,img_num]


        elif tag_num != 1 and self.list_flatten(img_zdx) == []:
            # 3.多个tag，且zdx tag下全为空(空将转化为'zdx')
            for i in range(len(img_all_list[zdx_num])):
                # 为zdx_txt 添加特有标志
                if img_all_list[zdx_num][i] == []:
                    img_all_list[zdx_num][i] = ['zdx']

            if tag_num == img_num:
                img_num_list = [zdx_num]

            elif tag_num > img_num:
                img_num_list = ['unknow']

            else:
                img_temp_list = self.list_flatten(img_all_list)
                if self.remove_duplication(img_temp_list) == ['zdx']:
                    if self.list_num(img_all_list) == img_num:
                        # 文本行数和图片数量一样
                        img_num_list = [self.list_finder('zdx',self.list_flatten_add_space(img_all_list))]
                        img_num_list = [i+1 for i in self.list_flatten(img_num_list)] # 每个元素+1
                    else:
                        # 文本行数和图片数量不一样
                        front_img_num = 0 # 非索引
                        for txt_temp_list in txt_all_list[:zdx_num]:
                            if txt_temp_list == []:
                                front_img_num = front_img_num + 1
                            for txt_temp in txt_temp_list:
                                front_img_num = front_img_num + self.txt_num(txt_temp)
                        front_img_num = front_img_num + 1
                        # behind_img_num_from_txt_num 为通过zdx有几则推断的 behind_img_num ，用于和之后的 behind_img_num 比较
                        try:
                            if txt_all_list[zdx_num] == []:
                                behind_img_num_from_txt_num = img_num
                            else:
                                behind_img_num_from_txt_num = front_img_num  + self.txt_num(''.join(self.list_flatten(txt[zdx_num][1]))) - 1
                        except:
                            print('error')


                        behind_img_num = 0
                        if len(txt_all_list) != zdx_num + 1:# zdx 不是txt尾
                            for txt_temp_list in txt_all_list[zdx_num+1:]:
                                if txt_temp_list == []:
                                    front_img_num = front_img_num + 1
                                for txt_temp in txt_temp_list:
                                    behind_img_num = behind_img_num + self.txt_num(txt_temp)
                        else:
                            behind_img_num = 0
                        behind_img_num = img_num - behind_img_num
                        if behind_img_num_from_txt_num > behind_img_num:
                            behind_img_num = behind_img_num_from_txt_num

                else:
                    front_img_num = 0  # 非索引
                    for i in range(len(txt_all_list[:zdx_num])):
                        for j in range(len(txt_all_list[:zdx_num][i])):
                            if img_all_list[:zdx_num][i][j] == []:
                                front_img_num = front_img_num + self.txt_num(txt_all_list[:zdx_num][i][j])
                    if self.list_finder('zdx',self.list_flatten(img_all_list))[0] - 1 >= 0:
                        front_img_num = front_img_num + 1 + self.list_flatten(img_all_list)[self.list_finder('zdx',self.list_flatten(img_all_list))[0] - 1]
                    else:
                        front_img_num = 1


                    behind_img_num = 0
                    if len(txt_all_list) != zdx_num + 1:
                        for i in range(len(txt_all_list[zdx_num + 1:])):
                            for j in range(len(txt_all_list[zdx_num + 1:][i])):
                                if img_all_list[zdx_num + 1:][i][j] == []:
                                    behind_img_num = behind_img_num + self.txt_num(txt_all_list[zdx_num + 1:][i][j])
                    else:
                        behind_img_num = 0
                    try:
                        behind_img_num = self.list_flatten(img_all_list)[self.list_finder('zdx',self.list_flatten(img_all_list))[-1] + 1] - 1
                        behind_img_num = img_num - behind_img_num
                    except:
                        pass
                    behind_img_num = img_num - behind_img_num

                if img_num_list == []:
                    img_num_list = [front_img_num, behind_img_num]


        elif tag_num != 1 and self.list_flatten(img_zdx) != []:
            # 4.多个tag，且zdx tag下部分为空(空将转化为'zdx')
            for i in range(len(img_all_list[zdx_num])):
                # 为zdx_txt 添加特有标志
                if img_all_list[zdx_num][i] == []:
                    img_all_list[zdx_num][i] = ['zdx']

            front_img_num = 0
            for i in range(len(img_all_list[zdx_num])):
                if img_all_list[zdx_num][i].isdigit() == True:
                    num_list.append(int(img_all_list[zdx_num][i].isdigit()))
            if num_list != []:
                front_img_num = min(num_list)

            behind_img_num = 0
            if len(txt_all_list) != zdx_num + 1:
                for i in range(len(txt_all_list[zdx_num + 1:])):
                    for j in range(len(txt_all_list[zdx_num + 1:][i])):
                        if img_all_list[zdx_num + 1:][i][j] == []:
                            behind_img_num = behind_img_num + self.txt_num(txt_all_list[zdx_num + 1:][i][j])
            else:
                behind_img_num = 0
            try:
                behind_img_num = self.list_flatten(img_all_list)[self.list_finder('zdx', self.list_flatten(img_all_list))[-1] + 1] - 1
                behind_img_num = img_num - behind_img_num
            except:
                pass
            behind_img_num = img_num - behind_img_num

            if img_num_list == []:
                img_num_list = [front_img_num, behind_img_num]


        print(txt)
        print(img_num_list)
        print('img: ' + str(img_num))
        print()



        return txt,img # 注意修改


if __name__ == '__main__':
    os.system(os.path.join(os.path.abspath('.'), 'deal_sql.py'))