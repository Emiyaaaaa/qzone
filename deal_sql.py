# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:12

import pymysql
import re
import copy
import os
import time
import urllib.request
from extra_apps.qzone.config.config import *


class DealSql():

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
        cursor.execute('SELECT id FROM qzone_html WHERE is_turned=0')
        html_list = []
        id_all = cursor.fetchall()

        if TEST_INFO != 0:
            id_all = id_all[:TEST_INFO]
        for id in id_all:
            cursor.execute('SELECT html,time FROM qzone_html WHERE id=' + str(id[0]))
            f = cursor.fetchall()
            html = f[0][0]
            time = f[0][1]
            if html == 'lhz':
                continue
            html_list.append({
                'html':html,
                'id':id[0],
                'time':time
            })

        return html_list


    def deal_html(self):

        html_list = self.extract_html()
        text_all_re = r'a href="http://rc.qzone.qq.com/qzonesoso/\?search=[\s\S]+?" target="_blank">#([\s\S]+?)#</a>([\s\S]+?)<'  # 小技巧：最开头去掉 <
        text_re = r'<a href="http://rc.qzone.qq.com/qzonesoso/\?search=%E6%89%BE%E5%AF%B9%E8%B1%A1&amp;entry=99&amp;businesstype=mood" target="_blank">#找对象#</a>([\s\S]+?)<'
        img_re = r'<a href="(http://b\d+.photo.store.qq.com/psb\?/.*?|http://m.qpic.cn/psb\?/.*?)"[\s\S]+?title="查看大图"'
        for html in html_list:
            txt = re.findall(text_all_re,html['html'])
            img = re.findall(img_re,html['html'])
            txt_img_list = DealAll().main(txt, img)
            self.up_sql(txt_img_list,html)


    def up_sql(self,txt_img_list,reason):
        cursor, connect = self.down_sql()
        cursor.execute('CREATE TABLE IF NOT EXISTS qzone_reason(id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,text LONGTEXT,time VARCHAR(50),timestamp VARCHAR(50))')
        my_time = reason['time']
        timeArray = time.strptime(my_time, "%Y年%m月%d日 %H:%M")
        time_stamp = time.mktime(timeArray)
        sql = 'INSERT INTO qzone_reason (text,time,timestamp) VALUES (%s,%s,%s)'
        cursor.execute(sql, (str(txt_img_list), my_time, time_stamp))
        cursor.execute('UPDATE qzone_html SET is_turned=1 WHERE id='+str(reason['id']))
        connect.commit()

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

    def img_num2img_url(self,txt_img_list,img):
        for list in txt_img_list:
            img_num = list[1][0]
            img_num = str(img_num).split(',')
            try:
                if img_num == '0':
                    list[1][0] = img
                elif len(img_num) == 1:
                    list[1][0] = img[int(img_num[0]) - 1]
                else:
                    list[1][0] = img[int(img_num[0])-1:int(img_num[1])-1]
            except:
                list[1][0] = img
        return txt_img_list


    def main(self,txt,img):
        # 结构[[[txt1],[img1]],[[txt2],[img2]]]
        # 获取self.deal_all()中的关键信息txt, img_num_list, img_num, txt_zdx, img_zdx
        tag_list = []
        txt_list = []
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
                        txt_img_list.append([[','.join(self.list_flatten(txt_zdx[i_last:i]))],[','.join('%s' %id for id in self.list_flatten(img_zdx[i_last:i]))]])
                        i_last = i
        else:
            txt_img_list.append([[','.join(self.list_flatten(txt_list))], [','.join('%s' % id for id in self.list_flatten(img_num_list))]])

        txt_img_list = self.img_num2img_url(txt_img_list,img)

        return txt_img_list


class GetMeasureWord():

    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species == None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self):
        if self.__first_init:
            try:
                url = 'http://xh.5156edu.com/page/z7949m2560j18586.html'
                url_txt = urllib.request.urlopen(url).read().decode('gbk')
                regular = r'<TD width=’11%’><A [\s\S]+?>([\S])</A></TD>'
                measure_word_list = re.findall(regular, url_txt)
                measure_word_list.append(u'位')
            except:
                measure_word_list = ['个','位','则','句','名']

            self.measure_word_list = measure_word_list
            self.__class__.__first_init = False


class DealTxtImg():
    # 当初能力有限，未能想到用中文正则表达式，尽早用正则表达式重构一遍

    def deal_txt_1(self,txt_one):  # 仅处理一行txt

        img_p = ['图', 'p', 'P']
        num = ['1', '2', '3', '4', '5', '6', '7', '8', '9','10','11','12','13','14', '一', '二', '三', '四', '五', '六', '七', '八', '九','十','十一','十二','十三','十四']
        to = ['-', '—', '到', '至', ',', '，', '、', '~', '.', ' ']
        and_ = [',', '.', '，', ' ']
        men = GetMeasureWord().measure_word_list
        sub_num = len(num)//2

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
                            if img_num_1 > sub_num:
                                img_num_1 = img_num_1 - sub_num
                            # 此处不宜支持十以上的判断
                            if len(txt_one) > img_p_num + 3:
                                if txt_one[img_p_num + 2] in num and txt_one[img_p_num + 3] in men:
                                    # 防止出现 p1一位... 时判断出[11]的错误结果
                                    break

                            # img_num_1 为 图img_num_1
                            if len(txt_one) > img_p_num + 3:  # 避免 string index out of range

                                try:
                                    # eg: 图一 —— 图二，图二——图五, 图三—— 六
                                    for i in range(4):
                                        if txt_one[img_p_num + i + 2] in to and txt_one[img_p_num + i + 3] in img_p and txt_one[img_p_num + i + 4] in num:
                                            img_num_2 = num.index(txt_one[img_p_num + i + 4]) + 1
                                            if img_num_2 > sub_num:
                                                img_num_2 = img_num_2 - sub_num
                                            remove_num = [img_p_num,img_p_num + i + 4]
                                            break
                                        elif txt_one[img_p_num + i + 2] in to and txt_one[img_p_num + i + 3] in num:
                                            if len(txt_one) > img_p_num + i + 4:
                                                if txt_one[img_p_num + i + 4] in men:
                                                    break
                                            img_num_2 = num.index(txt_one[img_p_num + i + 3]) + 1
                                            if img_num_2 > sub_num:
                                                img_num_2 = img_num_2 - sub_num
                                            remove_num = [img_p_num,img_p_num + i + 3]
                                            break
                                except:
                                    try:
                                        for i in range(4):
                                            if txt_one[img_p_num + i + 2] in to and txt_one[img_p_num + i + 3] in num:
                                                if len(txt_one) > img_p_num + i + 4:
                                                    if txt_one[img_p_num + i + 4] in men:
                                                        break
                                                img_num_2 = num.index(txt_one[img_p_num + i + 3]) + 1
                                                if img_num_2 > sub_num:
                                                    img_num_2 = img_num_2 - sub_num
                                                remove_num = [img_p_num, img_p_num + i + 3]
                                                break
                                    except:
                                        pass


                                if txt_one[img_p_num + 2] in to and txt_one[img_p_num + 3] in img_p:
                                    # eg: 图一,图二,图三,图四
                                    for i in range(1, len(txt_one) - img_p_num):
                                        if txt_one[img_p_num + i] in num and txt_one[img_p_num + i - 1] in img_p:
                                            img_num = num.index(txt_one[img_p_num + i]) + 1
                                            if img_num > sub_num:
                                                img_num = img_num - sub_num
                                            img_num_3.append(img_num)
                                            remove_num.append(img_p_num + i)
                                    break


                                elif txt_one[img_p_num + 2] in to and txt_one[img_p_num + 3] in num and txt_one[img_p_num + 2] not in and_:
                                    # eg: 图一~三，p1-3
                                    img_num_2 = num.index(txt_one[img_p_num + 3]) + 1
                                    if img_num_2 > sub_num:
                                        img_num_2 = img_num_2 - sub_num
                                    # 支持十以上的判断
                                    try:
                                        if ''.join([txt_one[img_p_num + 3],txt_one[img_p_num + 4]]) in num:
                                            img_num_2 = num.index(''.join([txt_one[img_p_num + 3],txt_one[img_p_num + 4]])) + 1
                                            if img_num_2 > sub_num:
                                                img_num_2 = img_num_2 - sub_num
                                            remove_num.append(img_p_num + 4)
                                    except:
                                        pass
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
                                            if img_num > sub_num:
                                                img_num = img_num - sub_num
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
                        if txt_one[0] not in num and txt_one[1] in num and txt_one[0].isalpha() == False:
                            fir_num_index = 1
                        elif txt_one[0] in num:
                            fir_num_index = 0
                        else:
                            break
                        for i in range(fir_num_index, len(txt_one)):
                            if txt_one[i] in num:
                                img_num = num.index(txt_one[i]) + 1
                                if len(txt_one) > i + 1:
                                    if txt_one[i] in num and txt_one[i + 1] in men:
                                        # 防止出现 p123一位... 时判断出[1231]的错误结果
                                        break
                                if img_num > sub_num:
                                    img_num = img_num - sub_num
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
        # 去掉文本中的入学年份
        txt = re.split(u'1[123456789]级', txt)
        txt = ''.join(txt)
        # 去掉文本中的出生年龄
        txt = re.split(u'[90][123456789][年后]', txt)
        txt = ''.join(txt)
        return txt

    def deal_img(self,num_list):

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

        return num_list


    def remove_txt(self,txt_one,remove_num):
        if remove_num == []:
            txt_one = txt_one
        else:
            txt_one = txt_one[:remove_num[0]]+txt_one[remove_num[-1]+1:]

        txt_one = (re.sub('[:：]', '', txt_one)) # 删掉类似'图一：'之类多余的字符串
        txt_one = txt_one.strip(',.，。') # 删除左边逗号等字符
        txt_one = txt_one.strip() # 删除两边空字符
        txt_one = txt_one.replace('\n','') # 好像没啥用啊
        # print(txt_one,len(txt_one))
        return txt_one


    def main(self,txt):

        img_list = []
        txt_n_new = []
        txt_n = re.split('\n', txt)  # txt_n 为 .split换行符后的 txt_list
        while '' in txt_n:
            txt_n.remove('')

        for txt_one in txt_n:
            img, remove_num = self.deal_txt_1(txt_one)
            txt_new = self.remove_txt(txt_one, remove_num)
            txt_n_new.append(txt_new)
            img_list.append(img)
        if txt_n == []:
            img_list = [[]]
        return txt_n_new, img_list


if __name__ == '__main__':
    DealSql().deal_html()