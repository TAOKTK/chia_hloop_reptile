#!/usr/bin/env python3

import os
import time
import subprocess
import datetime
import shutil
import requests
import json
import re
# 系统开始+++++++++++++
class ChiaStartUp():
    # 启动P盘程序
    def Main(self):
        # 当前位置
        base_dir = os.path.dirname(os.path.realpath(__file__))
        # 任务队列(处理并发的队列)
        chia_processes = []
        # 上个任务时间(时间戳)
        last_task_time = 0;
        # 第几个p盘并发程序
        number_of_current_tasks = 1;
        # 当前任务数据
        my_task_data = [];
        # 判断日志目录是否存在不存在则创建
        if not os.path.exists(f'{base_dir}/logs'):
            os.mkdir(f'{base_dir}/logs')
        try:
            while True:
                #请求任务(每分钟一次)
                my_task = self.GetApi({"action":"get_task"})
                print(my_task)

                # 没有任务
                if my_task['code'] != 0:
                    # 任务为空拦截
                    if my_task_data == []:
                        print("当前任务没有任务")
                        time.sleep(60)
                        continue
                    if my_task_data != []:
                        print("当前任务");
                        print(my_task_data);
                    print(f'请求返回{my_task["msg"]}')
                # 有任务需要执行(或者更换任务)
                if my_task['code'] == 0:
                    # 所有数据归零
                    chia_processes = []
                    last_task_time = 0;
                    number_of_current_tasks = 1;
                    my_task_data = my_task['data']
                # 执行新的P盘过程
                # 1.判断是否全部执行p盘
                if len(chia_processes) < my_task_data['plot_num']:
                    if last_task_time == 0:
                        plot_tmp = my_task_data['plot_tmp']+str(number_of_current_tasks)
                        plot_path = my_task_data['plot_path']
                        # 判断临时目录是否存在
                        if not os.path.exists(f'{plot_tmp}'):
                            os.makedirs(f'{plot_tmp}')
                        else:
                            shutil.rmtree(f'{plot_tmp}')
                            os.makedirs(f'{plot_tmp}')
                        if not os.path.exists(f'{plot_path}'):
                            os.mkdir(f'{plot_path}')
                        command = f'chia-plotter-windows-amd64 -action plotting -plotting-fpk {my_task_data["pool_public_key"]} -plotting-ppk {my_task_data["miner_public_key"]} -plotting-n {my_task_data["cycles"]} -b 3390 -d {plot_path} -t {plot_tmp} pause'
                        print(f'开始新的P盘过程: {command}')
                        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                        logfile = open(f'{base_dir}/logs/plot_{now}_{my_task_data["id"]}_{number_of_current_tasks}.log', 'w')
                        proc = subprocess.Popen(command.split(), stdout=logfile, stderr=logfile)
                        chia_processes.append(proc)
                        # 上个任务时间
                        last_task_time = int(time.time());
                        number_of_current_tasks = number_of_current_tasks+1
                    else:
                        # 判断任务是否大于间隔时间
                        if int(time.time()) - last_task_time >= my_task_data['intervals']:
                            plot_tmp = my_task_data['plot_tmp'] + str(number_of_current_tasks)
                            plot_path = my_task_data['plot_path']
                            # 判断临时目录是否存在
                            if not os.path.exists(f'{plot_tmp}'):
                                os.makedirs(f'{plot_tmp}')
                            else:
                                shutil.rmtree(f'{plot_tmp}')
                                os.makedirs(f'{plot_tmp}')
                            if not os.path.exists(f'{plot_path}'):
                                os.mkdir(f'{plot_path}')
                            command = f'chia-plotter-windows-amd64 -action plotting -plotting-fpk {my_task_data["pool_public_key"]} -plotting-ppk {my_task_data["miner_public_key"]} -plotting-n {my_task_data["cycles"]} -b 3390 -d {plot_path} -t {plot_tmp} pause'
                            print(f'开始新的P盘过程: {command}')
                            now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                            logfile = open(f'{base_dir}/logs/plot_{now}_{my_task_data["id"]}_{number_of_current_tasks}.log', 'w')
                            proc = subprocess.Popen(command.split(), stdout=logfile, stderr=logfile)
                            chia_processes.append(proc)

                            # 上个任务时间
                            last_task_time = int(time.time());
                            number_of_current_tasks = number_of_current_tasks + 1
                # 处理任务是否完成
                for p in chia_processes:
                    # 判断进程是否被终止
                    code = p.poll()
                    if code is not None:
                        plot_file = p.args[1].replace('.moving', '')
                        if code == 0:
                            print(f'success copy plot file: {plot_file}')
                        else:
                            print(f'failed copy plot file: {plot_file}')
                        print(f'一个P盘任务过程完成: {code}')
                        # 回调任务
                        my_callback = self.GetApi({"action": "callback","id": my_task_data['id'],'plot_file':plot_file})
                        print(my_callback)
                        # 触发子任务完成推送
                        chia_processes.remove(p)
                # 每60秒请求一次
                time.sleep(6)
        except Exception as e:
            print(f'error occurred: {e}')
    # 获取参数配置
    def Config(self):
        father_path = os.path.split(os.path.realpath(__file__))[0]
        config = open(father_path + "/config.json", 'r', encoding='utf-8')
        config_data = json.loads(re.sub("/\*.*\*/", "", config.read(), flags=re.MULTILINE))
        config.close()
        return config_data;
    # api接口请求
    def GetApi(self,content):
        # 配置参数
        config = self.Config()
        device_data = {
            "device_id": config["device_id"],
            "time": int(time.time()),
        }
        device_data_s = {**device_data,**content}
        # device_data['sign'] = md5(
        #     device_data['action'] + str(config["device_id"]) + str(config["device_key"]) + str(device_data['time']))
        return self.HttpPost(config["api_url"], device_data_s)
    # post请求
    def HttpPost(self, url, data):
        print(data)
        Number_of_attempts = 0
        while True:
            try:
                # 请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'close',
                }
                response = requests.post(url, data=data, headers=headers, timeout=200)
                return_data = response.json()
                break
            except Exception as e:
                print(e)
                Number_of_attempts += 1
                if Number_of_attempts > 10:
                    response = None
                    break
                time.sleep(3)
        return return_data
if __name__ == "__main__":
    print('开始执行!')
    ChiaStartUp = ChiaStartUp();
    ChiaStartUp.Main()
