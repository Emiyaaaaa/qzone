# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2018/5/8 20:12

import pymysql
import re

maxinfo = 30

class deal_sql(object):

    def down_sql(self):
        connect = pymysql.connect(host='127.0.0.1',
                                  port=3306,
                                  user='root',
                                  password='1234',
                                  charset='utf8',
                                  )
        cursor = connect.cursor()
        cursor.execute('USE qzone')

        return cursor,connect

    def extract_html(self):

        cursor,connect = self.down_sql()

        cursor.execute('SELECT id FROM qzone_html')
        id_all = cursor.fetchall()
        if id_all == ():
            print('请检查网络状态！')
        else:
            for id in id_all[:maxinfo]:
                cursor.execute('SELECT html FROM qzone_html WHERE id=' + str(id[0]))
                html = cursor.fetchall()[0][0]
                if html == 'lhz':
                    continue
                cursor.execute('SELECT time FROM qzone_html WHERE id=' + str(id[0]))
                time = cursor.fetchall()[0][0]
                txt,img = self.deal_html(html)
                self.up_sql(txt,img)


    def deal_html(self,html):


        text_all_re = r'a href="http://rc.qzone.qq.com/qzonesoso/\?search=[\s\S]+?" target="_blank">#([\s\S]+?)#</a>([\s\S]+?)<'  # 小技巧：最开头去掉 <
        text_re = r'<a href="http://rc.qzone.qq.com/qzonesoso/\?search=%E6%89%BE%E5%AF%B9%E8%B1%A1&amp;entry=99&amp;businesstype=mood" target="_blank">#找对象#</a>([\s\S]+?)<'
        img_re = r'<a href="(http://b\d+.photo.store.qq.com/psb\?/.*?|http://m.qpic.cn/psb\?/.*?)"[\s\S]+?title="查看大图"'

        txt = re.findall(text_all_re,html)
        img = re.findall(img_re,html)

        tag_list = []
        for txt_ in txt:
            tag_list.append(txt_[0])

        tag_all = len(txt)
        tag_num = tag_list.index('找对象')
        tag_zdx = txt[tag_num]
        zdx_txt = txt[tag_num][1]

        self.deal_txt_img_sim(zdx_txt)

        return txt,img

    def deal_txt_img_sim(self,txt):

        def deal_txt_1(txt_one): #仅处理一行txt

            img_p = ['图', 'p', 'P']
            num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '一', '二', '三', '四', '五', '六', '七', '八', '九']
            to = ['-', '—', '到', '至', ',', '，', '、', '~']
            and_ = [',', '.', '，', ' ']
            men = ['个','名','位']

            img_num_1 = 0 # 第一张图号
            img_num_2 = 0 # 第二张图号
            img_num_3 = [] # 两张或两张以上的图片的列表

            if txt_one != '\n' and txt_one != '</pre>':
                for img in img_p:
                    if img in txt_one[:3]: # 前三个字中有 img_p
                        img_p_num = txt_one.index(img) # img_p_num 为 img_p 的索引
                        if len(txt_one) > img_p_num+1: # 确保 img_p 不在最后一个字的位置
                            if txt_one[img_p_num+1] in num:
                                img_num_1 = num.index(txt_one[img_p_num+1])+1
                                if img_num_1 > 9:
                                    img_num_1 = img_num_1 - 9
                                # img_num_1 为 图img_num_1

                                if txt_one[img_p_num + 2] in to and txt_one[img_p_num + 3] in img_p and txt_one[img_p_num + 4] in num :
                                    # eg: 图一至图三，p1-p3，P1到P3
                                    img_num_2 = num.index(txt_one[img_p_num+4]) +1
                                    if img_num_2 > 9:
                                        img_num_2 = img_num_2 - 9
                                    break

                                elif txt_one[img_p_num+2] in img_p and txt_one[img_p_num + 3] in num :
                                    # eg: 图一图三，p1p3，P1P3
                                    img_num_2 = num.index(txt_one[img_p_num+3]) +1
                                    if img_num_2 > 9:
                                        img_num_2 = img_num_2 - 9
                                    break

                                elif txt_one[img_p_num + 2] in num :
                                    # eg: 图一三，p13，P13
                                    #     图一二三，p1234
                                    img_num_2 = num.index(txt_one[img_p_num+2]) +1
                                    if img_num_2 > 9:
                                        img_num_2 = img_num_2 - 9
                                    for i in range(1,len(txt_one)-img_p_num):
                                        if txt_one[img_p_num + i] in num :
                                            img_num = num.index(txt_one[img_p_num+i]) + 1
                                            if img_num > 9:
                                                img_num = img_num - 9
                                            img_num_3.append(img_num)
                                            if txt_one[img_p_num + i + 1] == '\n':
                                                break
                                    break

                                elif txt_one[img_p_num+2] in to and txt_one[img_p_num + 3] in num :
                                    # eg: 图一,二,三， p1,2,3， P1,3,5
                                    img_num_2 = num.index(txt_one[img_p_num+3]) +1
                                    if img_num_2 > 9:
                                        img_num_2 = img_num_2 - 9
                                    break

                                else:
                                # 转到其他tag处理函数
                                    pass

                            else:
                            # 转到其他tag处理函数
                                pass
                        else:
                            # 转到其他tag处理函数
                            pass

                    elif txt_one[0] in num or txt_one[0] in num:
                        # eg: 1.2.3.4
                        #     1234
                        if txt_one[0] == ' 'and txt_one [1] in num:
                            txt_num_index = txt_one
                        if len(txt_one)-img_p_num >= 15:
                            max_ = 15
                        else:
                            max_ = len(txt_one)-img_p_num
                        for i in range(2,max_):
                            if txt_one[img_p_num + i] in num:
                                img_num_3.append(i)


                else:
                    pass

            if img_num_2 == 0:
                img = img_num_1
            elif img_num_3 == []:
                img = [img_num_1,img_num_2]
            else:
                img = img_num_3
            return img


        img_list = []
        txt_n = re.split('\n', txt) # txt_n 为 .split换行符后的 txt_list
        while '' in txt_n:
            txt_n.remove('')

        for txt_one in txt_n:
            img = deal_txt_1(txt_one)
            img_list.append(img)
        print(txt,img_list)

        return txt,img_list


    def up_sql(self,txt,img):
        pass


if __name__ == '__main__':
    q = deal_sql()
    q.extract_html()