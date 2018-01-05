#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import os
import math
import time
import subprocess
import random
from PIL import Image


def is_around(_x, _y, _fix):
    return _x-_fix <= _y <= _x+_fix


def is_pix_around(_p1, _p2, _fix):
    c1 = is_around(_p1[0], _p2[0], _fix)
    c2 = is_around(_p1[1], _p2[1], _fix)
    c3 = is_around(_p1[2], _p2[2], _fix)
    return c1 and c2 and c3


def diff_pix(_p1, _p2):
    return "p1:%d, p2:%d, p3:%d" % ((_p1[0]-_p2[0]), (_p1[1]-_p2[1]), (_p1[2]-_p2[2]))


def draw_around(img_pix, x, y, step=5, color=(255, 0, 0)):
    for px in range(x-step, x+step+1):
        for py in range(y - step, y + step):
            if px > 0 and py > 0:
                img_pix[px, py] = color
    return img_pix


def head_judge(pix, color_fix):
    return is_pix_around(pix, (72, 59, 94, 255), color_fix) or \
            is_pix_around(pix, (120, 109, 154, 255), color_fix) or \
            is_pix_around(pix, (81, 76, 119, 255), color_fix) or \
            is_pix_around(pix, (56, 54, 70), color_fix)


def get_pos(_img, _img_des_path):
    mini_start_line_size = 25
    min_diff_y = 30

    img_width, img_height = _img.size
    img_pixel = _img.load()
    # find character
    print("img_height:%s, img_width:%s" % (str(img_height), str(img_width)))

    bak_pix = img_pixel[0, 203]
    print("bak_pix: " + str(bak_pix))
    if is_pix_around(bak_pix, (51, 49, 36), 20):
        _img.close()
        return -1, -1, -1, -1

    start_y = 0
    start_x = 0
    color_fix = 20

    rect_pix = None
    rect_top_list = list()

    y_start = 240
    for y in range(y_start, img_height):
        for x in range(img_width):
            pix = img_pixel[x, y]
            # 要排除棋子比方块高的情况
            if not head_judge(pix, color_fix):
                if not rect_pix and not is_pix_around(pix, bak_pix, color_fix):
                    # print("x:%s, y:%s, pix:%s" % (str(x), str(y), str(img_pixel[x, y])))
                    rect_pix = pix
                if rect_pix and not is_pix_around(pix, bak_pix, color_fix):
                    # print("x:%s, y:%s, pix:%s" % (str(x), str(y), str(img_pixel[x, y])))
                    rect_top_list.append([x, y])
        if rect_top_list and len(rect_top_list) >= mini_start_line_size:
            break
        elif rect_top_list:
            # print("@"*20)
            rect_top_list = []

    if len(rect_top_list) > 0:
        mid = rect_top_list[int(math.ceil(len(rect_top_list)/2))]
        # print("rect mid pos x: %d, y: %d, color:%s" % (mid[0], mid[1], str(img_pixel[mid[0], mid[1]])))
        start_x = mid[0]
        start_y = mid[1]
        rect_pix = img_pixel[start_x, start_y]

    # print("rect_top_list:" + str(rect_top_list)+"\n")
    print("start=>x:%d, y:%d" % (start_x, start_y))
    print("rect_pix: "+str(rect_pix))

    _tpx = _tpy = 0
    for y in range(start_y, img_height):
        for x in range(img_width):
            pixel = img_pixel[x, y]
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                _tpx = x
                _tpy = y
                break
        if _tpx > 0:
            break

    pix_path = list()
    pix_step = 5
    rx = start_x
    ry = start_y
    max_rx = rx
    max_ry_right = ry
    color_fix = 5
    while start_y <= ry <= img_width:
        while rx <= img_width:
            pix = img_pixel[rx, ry]
            if not is_pix_around(pix, rect_pix, color_fix):
                rx -= pix_step
                break
            else:
                pix_path.append((rx, ry))
                rx += pix_step
                max_ry_right = ry if rx > max_rx else max_ry_right
                max_rx = rx if rx > max_rx else max_rx

        if rx >= img_width:
            break
        # print("rx:%d, ry:%d" % (rx, ry))
        pix = img_pixel[rx, ry]
        if not is_pix_around(pix, rect_pix, color_fix):
            break
        else:
            ry += pix_step

    rx = start_x
    ry = start_y
    min_rx = rx
    max_ry_left = ry
    while start_y <= ry <= img_width:
        while rx >= 0:
            pix = img_pixel[rx, ry]
            if not is_pix_around(pix, rect_pix, color_fix):
                rx += pix_step
                break
            else:
                pix_path.append((rx, ry))
                rx -= pix_step
                max_ry_left = ry if rx < min_rx else max_ry_left
                min_rx = rx if rx < min_rx else min_rx

        if rx <= 0:
            break
        pix = img_pixel[rx, ry]
        if not is_pix_around(pix, rect_pix, color_fix):
            break
        else:
            ry += pix_step

    print("max_ry_left:%d, max_ry_right:%d" % (max_ry_left, max_ry_right))

    _next_x = start_x
    _next_y = max(max_ry_left, max_ry_right)

    max_y = 0
    min_y = start_y
    print("_next_y-start_y=%d-%d=%d " % (_next_y, start_y, _next_y - start_y))
    f_flag = (_next_y - start_y < min_diff_y)
    if f_flag:
        pix_step = 10
        color_fix = 10
        y_list = list()
        min_y_list_size = 15
        while True:
            pre_y = start_y
            # print("color_fix: "+str(color_fix))
            for y in range(start_y, img_height, pix_step):
                pix = img_pixel[start_x, y]
                if is_pix_around(pix, rect_pix, color_fix):
                    # print("#->x:%d, y:%d" % (start_x, y))
                    # print("p:%s, diff:%s" % (str(img_pixel[start_x, y]), str(diff_pix(pix, rect_pix))))
                    y_list.append(y)
                    # print("y-pre_y=%d-%d=%d" % (y, pre_y, (y-pre_y)))
                    if y - pre_y > pix_step * 5:
                        break
                    max_y = y if y > max_y else max_y
                    pre_y = y
            if len(y_list) < min_y_list_size:
                y_list = []
                color_fix += 1
                if color_fix > 30:
                    break
                max_y = 0
                min_y = start_y
                # print("~"*50)
            else:
                break
        max_y = min_y + 230 if max_y - min_y > 230 else max_y
        print("min_y:%d, max_y:%d" % (min_y, max_y))

        _next_x = start_x
        _next_y = int(math.ceil((min_y + max_y) / 2))

    print()
    print(" pos_x : %d,  pos_y : %d" % (_tpx, _tpy))
    print("next_x : %d, next_y : %d" % (_next_x, _next_y))

    draw_around(img_pixel, _tpx, _tpy, color=(255, 0, 0, 255))
    draw_around(img_pixel, _next_x, _next_y, color=(0, 255, 0, 255))
    if not f_flag:
        for item in pix_path:
            draw_around(img_pixel, item[0], item[1], color=(0, 0, 255, 255))
    else:
        draw_around(img_pixel, start_x, max_y, color=(0, 153, 68, 255))
    draw_around(img_pixel, start_x, start_y, color=(255, 255, 0, 255))

    # print("\n sth.")
    # ttx = 682
    # tty = 942
    # p_pix = img_pixel[ttx, tty]
    # print("(x:%d, y:%d):%s, diff:%s\n" % (ttx, tty, str(p_pix), str(diff_pix(p_pix, rect_pix))))

    _img.save(_img_des_path, 'PNG')
    _img.close()
    
    return _tpx, _tpy, _next_x, _next_y
    # return 0, 0, 0, 0


if __name__ == "__main__":

    debug = True  # False
    data_dir_name = "test_data" if debug else "data"
    base_path = "D:\\dev_lenovo\\python_tool\\" + data_dir_name + "\\"
    # base_path = "D:\\myjump\\" + data_dir_name + "\\"
    img_src_dir_path = base_path + "src"
    img_des_dir_path = base_path + "des"
    adb_path = "D:\\soft\\adb\\adb.exe"
    # adb_path = "D:\\wejump\\platform-tools\\adb.exe"

    if debug:
        print("base_path : " + base_path)
        img_file_list = os.listdir(img_src_dir_path)
        size = len(img_file_list)
        for img_index in range(size):
            img_name = img_file_list[img_index]
            print("%d/%d, img:%s" % ((img_index+1), size, img_name))
            img = Image.open(img_src_dir_path + os.sep + img_name)
            img_des_path = img_des_dir_path + os.sep + img_name
            get_pos(img, img_des_path)
            print("-" * 50)
    else:
        while True:
            img_name = "mx3_" + str(int(time.time())) + ".png"
            mx_img_path = "/sdcard/jump/" + img_name
            img_src_path = img_src_dir_path + os.sep + img_name
            img_des_path = img_des_dir_path + os.sep + img_name

            print("img: " + img_name)
            cmd = adb_path + " shell screencap -p " + mx_img_path
            # print(cmd)
            subprocess.call(cmd, shell=True)
            cmd = adb_path + " pull " + mx_img_path + " " + img_src_dir_path
            # print(cmd)
            subprocess.call(cmd, shell=True)
            cmd = adb_path + " shell \\rm " + mx_img_path
            # print(cmd)
            subprocess.call(cmd, shell=True)

            img = Image.open(img_src_dir_path + os.sep + img_name)

            tpx, tpy, next_x, next_y = get_pos(img, img_des_path)
            if tpx < 0:
                print("Game Over!")
                print("*" * 50)
                break

            dis = math.sqrt(math.pow(tpx - next_x, 2) + math.pow(tpx - next_x, 2))
            dis_time_set = 1.14
            duration = int(math.ceil(dis * dis_time_set))
            print("距离：%.2f, 距离系数：%.2f, 按压时间：%d" % (dis, dis_time_set, duration))
            cmd = adb_path + " shell input swipe {x1} {y1} {x2} {y2} {duration}".format(
                x1=tpx,
                y1=tpy,
                x2=tpx+1,
                y2=tpy+1,
                duration=duration
            )
            # print(cmd)
            subprocess.call(cmd, shell=True)

            print("*" * 50)
            t = int((5000 + int(math.ceil(5000*random.random())))/1000)
            print("sleep "+str(t)+"s")
            time.sleep(t)
            print("*"*50)

        print("Finish!")
