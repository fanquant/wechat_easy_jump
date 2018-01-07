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
    return _x - _fix <= _y <= _x + _fix


def is_pix_around(_p1, _p2, _fix):
    c1 = is_around(_p1[0], _p2[0], _fix)
    c2 = is_around(_p1[1], _p2[1], _fix)
    c3 = is_around(_p1[2], _p2[2], _fix)
    return c1 and c2 and c3


def diff_pix(_p1, _p2):
    return "c1:%d, c2:%d, c3:%d" % ((_p1[0] - _p2[0]), (_p1[1] - _p2[1]), (_p1[2] - _p2[2]))


def draw_around(img_pix, x, y, step=5, color=(255, 0, 0)):
    for px in range(x - step, x + step + 1):
        for py in range(y - step, y + step + 1):
            if px > 0 and py > 0:
                img_pix[px, py] = color


def head_judge(pix, color_fix):
    return is_pix_around(pix, (72, 59, 94, 255), color_fix) or \
           is_pix_around(pix, (120, 109, 154, 255), color_fix) or \
           is_pix_around(pix, (81, 76, 119, 255), color_fix) or \
           is_pix_around(pix, (56, 54, 70), color_fix) or \
           is_pix_around(pix, (200, 224, 222), color_fix) or \
           is_pix_around(pix, (184, 204, 203), color_fix)


def get_pos(_img, _img_des_path):
    mini_start_line_size = 25
    min_diff_y = 20

    img_width, img_height = _img.size
    img_pixel = _img.load()
    # find character
    # print("img_height:%s, img_width:%s" % (str(img_height), str(img_width)))

    bak_pix = img_pixel[0, 203]
    # print("bak_pix: " + str(bak_pix))
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
        mid = rect_top_list[int(math.ceil(len(rect_top_list) / 2))]
        # print("rect mid pos x: %d, y: %d, color:%s" % (mid[0], mid[1], str(img_pixel[mid[0], mid[1]])))
        start_x = mid[0]
        start_y = mid[1]
        rect_pix = img_pixel[start_x, start_y]

    # print("rect_top_list:" + str(rect_top_list)+"\n")
    # print("start=>x:%d, y:%d" % (start_x, start_y))
    # print("rect_pix: " + str(rect_pix))

    _tpx = _tpy = 0
    for y in range(start_y, img_height):
        for x in range(img_width):
            pixel = img_pixel[x, y]
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                _tpx = x
                _tpy = y + 2
                break
        if _tpx > 0:
            _tp_max_x = 0
            for x in range(_tpx + 1, img_width):
                pixel = img_pixel[x, _tpy]
                if not is_pix_around(pixel, (56, 56, 96, 255), color_fix):
                    _tp_max_x = x - 1
                    break
            _tpx = _tp_max_x - 37
            break

    pix_path = list()
    pix_step = 1
    rx = start_x
    ry = start_y
    max_rx = rx
    color_fix = 5
    max_ry_right = 0
    while start_y <= ry <= img_width - 1:
        while rx <= img_width - 1:
            pix = img_pixel[rx, ry]
            if not is_pix_around(pix, rect_pix, color_fix):
                rx -= pix_step
                break
            else:
                if rx >= max_rx:
                    pix_path.append((rx, ry))
                    max_rx = rx
                rx += pix_step

        if rx >= img_width:
            break
        # print("rx:%d, ry:%d" % (rx, ry))
        pix = img_pixel[rx, ry]
        if not is_pix_around(pix, rect_pix, color_fix):
            break
        else:
            ry += pix_step

    # 获取方块最有边像素的y的中间值
    rys = []
    pre = pix_path[len(pix_path)-1][0]
    for pp in range(len(pix_path)-1, 0, -1):
        px = pix_path[pp]
        if px[0] == pre:
            rys.append(px[1])
        else:
            break
        pre = px[0]
    if len(rys) > 0:
        max_ry_right = int((max(rys) + min(rys)) / 2)

    rx = start_x
    ry = start_y
    min_rx = rx
    max_ry_left = 0
    while start_y <= ry <= img_width - 1:
        while rx >= 0:
            pix = img_pixel[rx, ry]
            if not is_pix_around(pix, rect_pix, color_fix):
                rx += pix_step
                break
            else:
                if rx <= min_rx:
                    pix_path.append((rx, ry))
                    min_rx = rx
                rx -= pix_step
        if rx <= 0:
            break
        pix = img_pixel[rx, ry]
        if not is_pix_around(pix, rect_pix, color_fix):
            break
        else:
            ry += pix_step

    rys = []
    pre = pix_path[len(pix_path) - 1][0]
    for pp in range(len(pix_path) - 1, 0, -1):
        px = pix_path[pp]
        if px[0] == pre:
            rys.append(px[1])
        else:
            break
        pre = px[0]
    if len(rys) > 0:
        max_ry_left = int((max(rys) + min(rys)) / 2)

    # print("max_ry_left:%d, max_ry_right:%d" % (max_ry_left, max_ry_right))

    _next_x = start_x
    _next_y = t_y = max(max_ry_left, max_ry_right)

    max_y = 0
    min_y = start_y
    # print("border -> y:" + str(_next_y))
    # print("_next_y-start_y=%d-%d=%d min_diff_y=%d" % (_next_y, start_y, _next_y - start_y, min_diff_y))
    f_flag = (_next_y - start_y <= min_diff_y)

    # 一定要用方法2的 魔方/唱片机
    if is_pix_around(rect_pix, (107, 156, 248), 3) or is_pix_around(rect_pix, (168, 161, 154), 3):
        f_flag = True

    if f_flag:
        pix_step = 10
        color_fix = 10
        y_list = list()
        min_y_list_size = 25
        while True:
            _pre_y = start_y
            # print("color_fix: "+str(color_fix))
            for y in range(start_y, img_height, pix_step):
                pix = img_pixel[start_x, y]
                if is_pix_around(pix, rect_pix, color_fix):
                    # print("#->x:%d, y:%d" % (start_x, y))
                    # print("p:%s, diff:%s" % (str(img_pixel[start_x, y]), str(diff_pix(pix, rect_pix))))
                    y_list.append(y)
                    # print("y-pre_y=%d-%d=%d" % (y, pre_y, (y-pre_y)))
                    if y - _pre_y > pix_step * 5:
                        break
                    max_y = y if y > max_y else max_y
                    _pre_y = y
            if len(y_list) < min_y_list_size:
                y_list = []
                color_fix += 1
                if color_fix > 30:
                    break
                max_y = 0
                min_y = start_y
                # print("~" * 50)
            else:
                break
        max_y = min_y + 230 if max_y - min_y > 230 else max_y
        # print("line   -> min_y:%d, max_y:%d" % (min_y, max_y))

        _next_x = start_x
        _next_y = t_y if max_y - min_y > 250 else int(math.ceil((min_y + max_y) / 2))

        # WZC瓶子
        if is_pix_around(rect_pix, (255, 255, 255, 255), 10):
            f_flag = False
            _next_y = t_y

        # 音箱方块
        if f_flag:
            _next_y = int(math.ceil((start_y * 2 + 180) / 2)) if _next_y - min_y <= 25 else _next_y

    print(" pos_x : %d,  pos_y : %d" % (_tpx, _tpy))
    print("next_x : %d, next_y : %d" % (_next_x, _next_y))

    # 标记
    draw_around(img_pixel, _tpx, _tpy, color=(255, 0, 0, 255))
    draw_around(img_pixel, _next_x, _next_y, color=(0, 255, 0, 255))
    draw_around(img_pixel, start_x, max_y, color=(0, 255, 255, 255))
    for item in pix_path:
        # draw_around(img_pixel, item[0], item[1], step=0, color=(0, 0, 255, 255))
        img_pixel[item[0], item[1]] = (0, 0, 255, 255)
    draw_around(img_pixel, start_x, start_y, color=(255, 255, 0, 255))
    img_pixel[_tpx, _tpy] = (0, 0, 0, 255)

    # print("\n sth.")
    # ttx = 448
    # tty = 820
    # p_pix = img_pixel[ttx, tty]
    # print("###-> (x:%d, y:%d):%s, diff:%s\n" % (ttx, tty, str(p_pix), str(diff_pix(p_pix, rect_pix))))

    _img.save(_img_des_path, 'PNG')
    _img.close()

    return _tpx, _tpy, _next_x, _next_y


if __name__ == "__main__":

    debug = not True
    data_dir_name = "test_data" if debug else "data"
    base_path = "D:\\dev_lenovo\\python_tool\\" + data_dir_name + "\\"
    base_path = "D:\\myjump\\" + data_dir_name + "\\"
    img_src_dir_path = base_path + "src"
    img_des_dir_path = base_path + "des"
    adb_path = "D:\\soft\\adb\\adb.exe"
    adb_path = "D:\\wejump\\platform-tools\\adb.exe"

    if debug:
        print("base_path : " + base_path)
        img_file_list = os.listdir(img_src_dir_path)
        size = len(img_file_list)
        print("-" * 50)
        for img_index in range(size):
            s_t = time.time()
            img_name = img_file_list[img_index]
            print("%d/%d, %.2f%%, img:%s" % ((img_index + 1), size, float(img_index+1)/size*100, img_name))
            print()
            img = Image.open(img_src_dir_path + os.sep + img_name)
            img_des_path = img_des_dir_path + os.sep + img_name
            get_pos(img, img_des_path)
            s_t = time.time() - s_t
            print()
            print("time spend:%ds" % s_t)
            print("-" * 50)
    else:
        step_counter = 0
        print("*" * 50)
        while True:
            step_counter += 1
            print("step no : %d" % step_counter)

            print("datetime : " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            img_name = "mx3_" + str(int(time.time())) + ".png"
            mx_img_path = "/sdcard/jump/" + img_name
            img_src_path = img_src_dir_path + os.sep + img_name
            img_des_path = img_des_dir_path + os.sep + img_name

            print("img : " + img_name)
            cmd = adb_path + " shell screencap -p " + mx_img_path + " > null"
            # print(cmd)
            subprocess.call(cmd, shell=True)
            cmd = adb_path + " pull " + mx_img_path + " " + img_src_dir_path + " > null"
            # print(cmd)
            subprocess.call(cmd, shell=True)
            cmd = adb_path + " shell \\rm " + mx_img_path + " > null"
            # print(cmd)
            subprocess.call(cmd, shell=True)
            # print()

            img = Image.open(img_src_dir_path + os.sep + img_name)

            tpx, tpy, next_x, next_y = get_pos(img, img_des_path)
            if tpx < 0:
                print("*" * 50)
                print("Game Over!")
                print("*" * 50)
                break

            dis = math.sqrt(math.pow(tpx - next_x, 2) + math.pow(tpx - next_x, 2))
            dis_time_set = random.uniform(1.12, 1.16)
            duration = int(dis * dis_time_set)
            if duration < 120:
                time.sleep(20)
                continue

            print("dis : %.2f, fix : %.2f, press time : %dms" % (dis, dis_time_set, duration))
            cmd = adb_path + " shell input swipe {x1} {y1} {x2} {y2} {duration}".format(
                x1=tpx,
                y1=tpy,
                x2=tpx + 1,
                y2=tpy + 1,
                duration=duration
            )
            # print(cmd)
            subprocess.call(cmd, shell=True)

            print("*" * 50)
            t = random.randint(5, 8)
            print("sleep " + str(t) + "s")
            time.sleep(t)
            print("*" * 50)

        # print("Finish!")
