# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/27 14:49

import re
import os

class DealTxtImg():
    # 当初能力有限，未能想到用中文正则表达式，尽量早日用正则表达式重构一遍

    def deal_txt_1(self,txt_one):  # 仅处理一行txt

        img_p = ['图', 'p', 'P']
        num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '一', '二', '三', '四', '五', '六', '七', '八', '九']
        to = ['-', '—', '到', '至', ',', '，', '、', '~', '.', ' ']
        and_ = [',', '.', '，', ' ']
        men = ['个', '名', '位', '则']

        img_num_1 = 0  # 第一张图号
        img_num_2 = 0  # 第二张图号
        img_num_3 = []  # 两张或两张以上的图片的列表
        remove_num = []  # 删除p1图一等内容, 注意：元素为索引

        if txt_one != '\n' and txt_one != '</pre>' and txt_one != '':
            txt_one = self.del_else(txt_one)  # 去掉文本中的身高,年级
            for img in img_p:
                # 在适当位置添加break以减少不必要的循环
                if img in txt_one:  # if img in txt_one[:3]:  前三个字中有 img_p
                    img_p_num = txt_one.index(img)  # img_p_num 为 img_p 的索引
                    if len(txt_one) > img_p_num + 1:  # 确保 img_p 不在最后一个字的位置

                        if txt_one[img_p_num + 1] in num:
                            img_num_1 = num.index(txt_one[img_p_num + 1]) + 1
                            remove_num.append(img_p_num)
                            remove_num.append(img_p_num+1)
                            if img_num_1 > 9:
                                img_num_1 = img_num_1 - 9
                            if len(txt_one) > img_p_num + 3:
                                if txt_one[img_p_num + 2] in num and txt_one[img_p_num + 3] in men:
                                    # 防止出现 p1一位... 时判断出[11]的错误结果
                                    break

                            # img_num_1 为 图img_num_1
                            if len(txt_one) > img_p_num + 3:  # 避免 string index out of range

                                if txt_one[img_p_num + 2] in to and txt_one[img_p_num + 3] in img_p:
                                    # eg: 图一,图二,图三,图四
                                    for i in range(1, len(txt_one) - img_p_num):
                                        if txt_one[img_p_num + i] in num and txt_one[img_p_num + i - 1] in img_p:
                                            img_num = num.index(txt_one[img_p_num + i]) + 1
                                            if img_num > 9:
                                                img_num = img_num - 9
                                            img_num_3.append(img_num)
                                            remove_num.append(img_p_num + i)
                                    break


                                elif txt_one[img_p_num + 2] in to and txt_one[img_p_num + 3] in num and txt_one[img_p_num + 2] not in and_:
                                    # eg: 图一~三，p1-3
                                    img_num_2 = num.index(txt_one[img_p_num + 3]) + 1
                                    if img_num_2 > 9:
                                        img_num_2 = img_num_2 - 9
                                    remove_num.append(img_p_num + 3)
                                    break


                                elif txt_one[img_p_num + 1] in num:
                                    # eg: 图一三，p13，P13
                                    #     图一二三，p1234
                                    #     图一,二,三， p1,2,3， P1,3,5
                                    #     图一图二图三
                                    for i in range(1, len(txt_one) - img_p_num):
                                        if txt_one[img_p_num + i] in num:
                                            img_num = num.index(txt_one[img_p_num + i]) + 1
                                            if len(txt_one) > img_p_num + i + 1: # 防止数组越界
                                                if txt_one[img_p_num + i] in num and txt_one[img_p_num + i + 1] in men:
                                                    # 防止出现 p123一位... 时判断出[1231]的错误结果
                                                    break
                                            if img_num > 9:
                                                img_num = img_num - 9
                                            img_num_3.append(img_num)
                                            remove_num.append(img_p_num + i)
                                        elif txt_one[img_p_num + i] not in num and txt_one[img_p_num + i] not in and_ and txt_one[img_p_num + i] not in img_p:
                                            # 既不是123 也不是，.，
                                            break
                                    break


                elif len(txt_one) >= 2 and txt_one[0] not in img_p:
                    if txt_one[0] in num or txt_one[1] in num:
                        # eg: 1.2.3.4  1234
                        #     一二三四   一，二，三
                        #     1-3    2~5
                        if txt_one[0] not in num and txt_one[1] in num:
                            fir_num_index = 1
                        elif txt_one[0] in num:
                            fir_num_index = 0
                        for i in range(fir_num_index, len(txt_one)):
                            if txt_one[i] in num:
                                img_num = num.index(txt_one[i]) + 1
                                if len(txt_one) > i + 1:
                                    if txt_one[i] in num and txt_one[i + 1] in men:
                                        # 防止出现 p123一位... 时判断出[1231]的错误结果
                                        break
                                if img_num > 9:
                                    img_num = img_num - 9
                                img_num_3.append(img_num)
                                remove_num.append(i)
                            elif txt_one[i] not in num and txt_one[i] not in to:
                                # 既不是123 也不是，.，
                                break
                    break

                else:
                    pass

        if img_num_3 != []:
            img = img_num_3
        elif img_num_2 == 0:
            img = [img_num_1]
        else:
            img = [img_num_1, img_num_2]
        img = self.deal_img(img)

        return img,remove_num

    def del_else(self,txt_one):

        # 去掉文本中的身高
        txt = re.split(r'1[5678]\d', txt_one)
        txt = ''.join(txt)
        # 去掉文本中的年级
        txt = re.split(u'大[一二三四]', txt)
        txt = ''.join(txt)
        return txt

    def deal_img(self,img):

        num_ini = 0
        if img != [] and img != 0:
            # 有序去重
            img_list = []
            for i in img:
                if i not in img_list:
                    img_list.append(i)
            img = img_list

            for num in img:
                if num <= num_ini:
                    img.remove(num)
                else:
                    num_ini = num

        return img

    def remove_txt(self,txt_one,remove_num):
        if remove_num == []:
            txt_one = txt_one
        else:
            txt_one = txt_one[:remove_num[0]]+txt_one[remove_num[-1]+1:]

        txt_one = (re.sub('[:：]', '', txt_one)) # 删掉类似'图一：'之类多余的字符串
        txt_one = txt_one.strip(',.，。') # 删除左边逗号等字符
        txt_one = txt_one.strip() # 删除两边空字符
        return txt_one


    def main(self,txt):

        img_list = []
        txt_n = re.split('\n', txt)  # txt_n 为 .split换行符后的 txt_list
        while '' in txt_n:
            txt_n.remove('')

        if txt_n == []:
            img_list = [[]]
        for txt_one in txt_n:
            img, remove_num = self.deal_txt_1(txt_one)
            img_list.append(img)

        return txt_n, img_list

if __name__ == '__main__':
    os.system(os.path.join(os.path.abspath('.'),'deal_sql.py'))