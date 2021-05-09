#!/usr/bin/env python3

import glob
import os
import time
import subprocess
import datetime

# 启动 P 盘数量
plot_num = 2
# 临时文件目录
plot_tmp = "/data/chia/tmp"
# 最终文件目录
plot_path = "/data/chia/plots"
farmer_key = ""
pool_key = ""

# 是否启用远程复制
remote_enable = True
remote_user = "root"
remote_ip = "192.168.0.12"
remote_path = "/data/chia/plots"


def main():
    try:
        chia_processes = []
        scp_processes = []
        base_dir = os.path.dirname(os.path.realpath(__file__))

        if not os.path.exists(f'{base_dir}/logs'):
            os.mkdir(f'{base_dir}/logs')

        while True:
            # 删除完成的过程
            for p in chia_processes:
                code = p.poll()
                if code is not None:
                    print(f'one plot process finished with code: {code}')
                    chia_processes.remove(p)

            # 开始新的过程
            if len(chia_processes) < plot_num:
                command = f'chia plots create -k 32 -t {plot_tmp} -d {plot_path} -r 2 -n 1 -f {farmer_key} -p {pool_key}'
                print(f'start new plat process: {command}')
                now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                logfile = open(f'{base_dir}/logs/plot_{now}.log', 'w')
                proc = subprocess.Popen(command.split(), stdout=logfile, stderr=logfile)
                chia_processes.append(proc)

            #将绘图文件复制到远程
            if remote_enable:
                # 检查scp进程
                for p in scp_processes:
                    code = p.poll()
                    if code is not None:
                        plot_file = p.args[1].replace('.moving', '')
                        if code == 0:
                            print(f'success copy plot file: {plot_file}')
                            os.remove(p.args[1])
                        else:
                            print(f'failed copy plot file: {plot_file}')
                            os.rename(p.args[1], plot_file)
                        scp_processes.remove(p)

                # 开始新的SCP过程
                if len(scp_processes) < 2:
                    for f in glob.glob(f'{plot_path}/*.plot'):
                        file_name = f.split('/')[-1]
                        remote_file = f'{remote_user}@{remote_ip}:{remote_path}/{file_name}'
                        moving_path = f + ".moving"
                        os.rename(f, moving_path)
                        print(f'start copy plot: {f}')
                        logfile = open(f'{base_dir}/logs/scp_{file_name}.log', 'w')
                        proc = subprocess.Popen(['scp', moving_path, remote_file], stdout=logfile, stderr=logfile)
                        scp_processes.append(proc)

                        break

            time.sleep(300)
    except Exception as e:
        print(f'error occurred: {e}')


if __name__ == "__main__":
    print('start rock !')
    main()
