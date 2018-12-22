# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:12

import pymysql
import re
import copy
from deal_zdx_txt import DealTxtImg
from config.config import *

class DealSql(object):

    def down_sql(self):
        connect = pymysql.connect(
            host=DATABASES['HOST'],
            port=3306,
            user=DATABASES['USER'],
            password=DATABASES['PASSWORD'],
            charset='utf8mb4',
        )
        cursor = connect.cursor()
        cursor.execute('USE qzone')

        return cursor,connect

    def extract_html(self):

        cursor,connect = self.down_sql()
        cursor.execute('SELECT id FROM qzone_html')
        html = ''
        id_all = cursor.fetchall()
        if id_all == ():
            print('请检查网络状态！')
        else:
            for id in id_all[:TEST_INFO]:
                cursor.execute('SELECT html FROM qzone_html WHERE id=' + str(id[0]))
                html = cursor.fetchall()[0][0]
                if html == 'lhz':
                    continue
                cursor.execute('SELECT time FROM qzone_html WHERE id=' + str(id[0]))
                time = cursor.fetchall()[0][0]
        return html


    def deal_html(self):

        html = self.extract_html()
        text_all_re = r'a href="http://rc.qzone.qq.com/qzonesoso/\?search=[\s\S]+?" target="_blank">#([\s\S]+?)#</a>([\s\S]+?)<'  # 小技巧：最开头去掉 <
        text_re = r'<a href="http://rc.qzone.qq.com/qzonesoso/\?search=%E6%89%BE%E5%AF%B9%E8%B1%A1&amp;entry=99&amp;businesstype=mood" target="_blank">#找对象#</a>([\s\S]+?)<'
        img_re = r'<a href="(http://b\d+.photo.store.qq.com/psb\?/.*?|http://m.qpic.cn/psb\?/.*?)"[\s\S]+?title="查看大图"'

        txt = re.findall(text_all_re,html)
        img = re.findall(img_re,html)

        return txt,img


    def up_sql(self,txt,img):
        pass


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

    def list_flatten_add_space_2(self, l):
        # 将二维数组转化为一维数组,并将空元素转化为空格
        l_copy = copy.deepcopy(l)
        for i in range(len(l_copy)):
                if l_copy[i] == []:
                    l_copy[i] = [' ']
        l_copy = self.list_flatten(l_copy)
        return l_copy


    def list_flatten_add_space(self, l):
        # 将三维数组转化为一维数组,并将空元素转化为空格
        l_copy = copy.deepcopy(l)
        for i in range(len(l_copy)):
            for j in range(len(l_copy[i])):
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

        if self.list_flatten(img_zdx) != []:
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
                img_num_list = [1,img_num]

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
                            behind_img_num_from_txt_num = 0
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

        return [zdx_txt],img_num_list # 注意修改


    def deal_num(self,num_list):
        # 数字list处理,大小先后顺序，去重等
        num_ini = 0
        if num_list != [] and num_list != 0:
            # 有序去重
            img_list = []
            for i in num_list:
                if i not in img_list:
                    img_list.append(i)
            num_list = img_list

            for num in num_list:
                if num <= num_ini:
                    num_list.remove(num)
                else:
                    num_ini = num

        num_list = [num_list[0],num_list[-1]]

        return num_list


    def main(self,txt,img):
        # 结构[[[txt1],[img1]],[[txt2],[img2]]]

        # 获取self.deal_all()中的关键信息txt, img_num_list, img_num, txt_zdx, img_zdx
        tag_list = []
        img_num = len(img)
        for txt_ in txt:
            tag_list.append(txt_[0])
        zdx_num = tag_list.index('找对象')
        zdx_txt = txt[zdx_num][1]
        txt_zdx, img_zdx = DealTxtImg().main(zdx_txt)
        try:
            txt_list, img_num_list = self.deal_all(txt,img)
        except:
            img_num_list = [1,img_num]

        txt_img_list = []
        group_list = []
        i_last = 0
        if self.list_flatten(img_zdx) != []:
            if ' ' not in self.list_flatten_add_space_2(img_zdx):
                for i in range(len(txt_zdx)):
                    txt_img_list.append([[txt_zdx[i]],img_zdx[i]])
            else:
                for i in range(len(txt_zdx)):
                    if img_zdx[i] != []:
                        group_list.append(i)
                if len(group_list) == 1:
                    txt_img_list.append([[','.join(self.list_flatten(txt_zdx))],[','.join('%s' %id for id in self.list_flatten(img_zdx))]])
                else:
                    group_list.append(len(img_zdx))
                    for i in group_list[1:]:
                        print(group_list)
                        txt_img_list.append([[','.join(self.list_flatten(txt_zdx[i_last:i]))],[','.join('%s' %id for id in self.list_flatten(img_zdx[i_last:i]))]])
                        i_last = i
        else:
            txt_img_list.append([[','.join(self.list_flatten(txt_list))], [','.join('%s' % id for id in self.list_flatten(img_num_list))]])

        print(txt)
        print(txt_zdx)
        print(img_num)
        print(txt_img_list)
        print()
        return txt_img_list


if __name__ == '__main__':
    DealSql().extract_html()