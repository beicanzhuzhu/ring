# -*- coding: utf-8 -*-

from datetime import datetime
from reprint import output
import time
import platform
import os
import json

# 使输出支持ansi转义序列
if platform.system() == "Windows":
    os.system("color")

try:
    from playsound import playsound
except ModuleNotFoundError:
    print("\033[0;31m", end="")
    print('未检测到 playsound 模块，因此无法运行此程序')
    print('请安装 playsound 后重启此程序')
    print("\033[0m")
    exit(1)

# 导入配置文件
try:
    with open("settings.json") as se:
        settings = json.load(se)
except FileNotFoundError:
    se = open("settings.json", "w")
    settings = {
        "alarm_clock_path": "ring.mp3",
        "ring_path": "ring.mp3",
        "default_schedule": "",
        "remind_you_ahead_of_time_to_start_the_event": 10,
        "remind_you_ahead_of_time_to_end_the_event": 10,
        "schedule_height": 30,
        "schedule_wide": 80
    }
    # indent=0格式化字典
    json.dump(settings, se, indent=0)

print('自定义时间打铃器v2.1')
try:
    open(settings["ring_path"])
except FileNotFoundError:
    print("\033[0;31m", end="")
    print("未找到音频文件\033[4m" + settings["alarm_clock_path"] + "\033[0;31m，请检查settings.json文件")
    print("\033[0m", end="")
    exit(1)
try:
    open(settings["alarm_clock_path"])
except FileNotFoundError:
    print("\033[0;31m", end="")
    print("未找到音频文件\033[4;31m" + settings["alarm_clock_path"] + "\033[0;31m，请检查settings.json文件")
    print("\033[0m", end="")
    exit(1)

print('现在开始设置时间表')
print('请输入序号选择时间表或新建时间表。')

# 如果存放时间表的schedules文件夹不存在则创建一个
if not os.path.exists("schedules\\"):
    os.mkdir("schedules\\")

# 读取文件
schedules = os.listdir("schedules\\")

# 在列表中去除非时间表文件
for i in schedules:
    if not i.endswith(".schedule.json"):
        schedules.remove(i)

for i in range(0, len(schedules)):
    print(str(i + 1) + ") " + schedules[i].replace(".schedule.json", ""))
print(str(len(schedules) + 1) + ") 新建时间表")

while True:
    schedule_name = ""
    n = input("输入：")
    try:
        n = int(n)
    except ValueError:
        print("请输入1~" + str(len(schedules) + 1) + "的整数")
        continue

    if 0 < n <= len(schedules):
        # 读取对应时间表
        schedule_name = schedules[n - 1]
        break
        # 时间表选择完成，进入运行阶段

    elif n == len(schedules) + 1:
        # 新建时间表
        a = 1

    else:
        print("请输入1~" + str(len(schedules) + 1) + "的整数")

with open("schedules\\" + schedule_name) as fp:
    schedule = json.load(fp)

# 检测时间表是否合法
for t in range(0, len(schedule)):

    try:
        _ = datetime.strptime(schedule[t]["time_start"], "%H:%M")
    except ValueError:
        print("时间表：")
        print(t)
        print("中存在一个非法的时间或表达")
        exit(-1)
    except KeyError:
        print("时间表：")
        print(t)
        print("中存在一个非法的键")
        exit(-1)

    if schedule[t]["time_end"] != "null":
        try:
            _ = datetime.strptime(schedule[t]["time_end"], "%H:%M")
        except ValueError:
            print("时间表：")
            print(t)
            print("中存在一个非法的时间或表达")
            exit(-1)
        except KeyError:
            print("时间表：")
            print(t)
            print("中存在一个非法的键")
            exit(-1)


# 统计word中中文字符的数量
def chinese_number(word) -> int:
    number = 0
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            number += 1
    return number


def time_difference(a_hour, a_minute, b_hour, b_minute) -> int:
    return (b_hour - a_hour) * 60 + b_minute - a_minute


os.system("cls")

doing_things = []  # 正在进行的事
alarm_clock = []  # 闹钟时件
start_soon = []  # 即将开始

with output(output_type="list",
            initial_len=settings["schedule_height"],
            interval=0) as output_list:
    while True:

        # 打印当前时间
        output_list_index = 0
        _ = datetime.now()
        # 保存当前时间
        time_now = (_.hour, _.minute, _.second)

        #  判定时间
        for user_time in schedule:
            # 使用变量将字符串转化为元组，方便比较
            user_start_time = (datetime.strptime(user_time["time_start"], "%H:%M").hour,
                               datetime.strptime(user_time["time_start"], "%H:%M").minute)
            user_end_time = (datetime.strptime(user_time["time_end"], "%H:%M").hour,
                             datetime.strptime(user_time["time_end"], "%H:%M").minute) \
                if user_time["time_end"] != "null" else "null"
            # 闹钟事件
            if user_start_time == time_now[0:2] and user_time["time_end"] == "null":
                alarm_clock.append(user_time)

            # 即将开始的事
            if 0 < time_difference(time_now[0], time_now[1], user_start_time[0], user_start_time[1]) <= settings["remind_you_ahead_of_time_to_start_the_event"]:
                if user_time not in start_soon:
                    start_soon.append(user_time)

            # 正在进行的事
            if user_time["time_end"] != "null" and user_start_time <= time_now <= user_end_time:
                # 从即将到来的事列表中删除
                if user_time in start_soon:
                    start_soon.remove(user_time)
                # 添加到正在进行的事
                if user_time not in doing_things:
                    # playsound(settings["ring_path"])
                    print("\a\a\a", end="")
                    doing_things.append(user_time)
            # 结束后从列表中删除
            if user_time["time_end"] != "null" and time_now > user_end_time and user_time in doing_things:
                print("\a", end="")
                doing_things.remove(user_time)
                for i in range(0, settings["schedule_height"]):
                    output_list[i] = ""

        # 输出
        output_list[output_list_index] = (datetime.strftime(_, "%Y-%m-%d %H:%M:%S"))
        output_list_index += 1
        output_list[output_list_index] = ("{:*^" + str(80 + 8) + "}").format(
            "\033[0;33m时间表\033[0m")
        output_list_index += 1

        # 处理闹钟
        if alarm_clock:
            for i in alarm_clock:
                _ = datetime.strptime(i["time_start"], "%H:%M")
                start_minute = _.minute
                # 输出样式
                # *闹钟:somthing                     |                            00:00*
                output_list[output_list_index] = (
                        "*{: <" + str(80 - 2 - chinese_number(i["action"])) + "}|{: >" + str(
                    80) + "}*") \
                    .format("闹钟:" + i["action"], i["time_start"])
                output_list_index += 1
                # *已超过                                                              *
                output_list[output_list_index] = ("*{:<" + str(80 - 5) + "}*") \
                    .format("已超过" + str(time_now[1] - start_minute)
                            + "分" + str(time_now[2]) + "秒")
                output_list_index += 1
                # *********************************************************************
                output_list[output_list_index] = ("{:*^" + str(80) + "}").format("")
                output_list_index += 1
        if doing_things:
            for i in doing_things:
                _ = datetime.strptime(i["time_start"], "%H:%M")
                start_hour = _.hour
                start_minute = _.minute
                _ = datetime.strptime(i["time_end"], "%H:%M")
                end_hour = _.hour
                end_minute = _.minute
                last_minute = time_difference(start_hour, start_minute, end_hour, end_minute)
                # 输出样式
                # *somthing                     |                        00：00~00：00*
                output_list[output_list_index] = ("*{: <" + str(
                    80 - 42 - chinese_number(i["action"])) + "}|{: >39}*") \
                    .format(i["action"], i["time_start"] + "~" + i["time_end"])
                output_list_index += 1
                # 进度条样式
                # *=============>               |剩余00:00:00 已过00:00:00 总共00:00:00*
                output_list[output_list_index] = ("*{: <" + str(80 - 42) + "}|{: >35}*") \
                    .format(
                    "=" * int(time_difference(start_hour, start_minute, time_now[0], time_now[1]) / last_minute * (
                            80 - 42)) + ">",
                    "剩余:" + (str(time_difference(time_now[0], time_now[1], end_hour, end_minute) // 60)) + "时" + str(
                        time_difference(time_now[0], time_now[1], end_hour, end_minute) % 60) + "分")
                output_list_index += 1
                # *********************************************************************
                output_list[output_list_index] = "{:*^80}".format("")
                output_list_index += 1

        if start_soon:
            for i in start_soon:
                _ = datetime.strptime(i["time_start"], "%H:%M")
                start_hour = _.hour
                start_minute = _.minute
                output_list[output_list_index] = ("*{: <" + str(
                    80 - 46 - chinese_number(i["action"])) + "}|{: >36}*").format("即将开始:" + i["action"],
                                                                                  "剩余:" + str(
                                                                                      time_difference(time_now[0], time_now[1], start_hour, start_minute)) + "分")
                output_list_index += 1
                output_list[output_list_index] = "{:*^80}".format("")
                output_list_index += 1

        time.sleep(0.2)

        #
