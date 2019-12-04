#! /usr/bin/env python3
# @author yanjiujun@gmail.com 
# @date 2019-12-4
# 开启自动关闭显示器，只要本机ip地址是预设的ip。我们可以通过路由器的dhcp来控制本机的ip
# 从而决定是否关闭显示器。平时是关闭的，一旦遇到非要点亮屏幕才能调试的情况，就可以改变
# dhcp中的本机ip，重启系统后会点亮屏幕。

import socket
import sys
import os
import time
import getopt
import traceback
import urllib.request
import urllib.error
import platform
import ssl
import json
import psutil

IP = '192.168.0.11'

def set_daemonize():
    '''
        变为后台程序。
    '''
    # /dev/null 必须是全剧的，不然会被自动释放，导致后面的文件打开各种悲剧
    global file_null
    try:
        pid = os.fork()
        if pid:
            exit(0)
    except OSError as e:
        print('fork() 调用错误！')

    os.setsid()

    try:
        pid = os.fork()
        if pid:
            exit(0)
    except OSError as e:
        print('fork() 调用错误！')
    
    # 将标准输出输出标准出错全都重定向到null文件中
    file_in = open('/dev/null','r')
    file_out = open('/dev/null','a+')
    file_err = open('/dev/null','a+')
    
    os.dup2(file_in.fileno(),sys.stdin.fileno())
    os.dup2(file_out.fileno(),sys.stdout.fileno())
    os.dup2(file_err.fileno(),sys.stderr.fileno())
    
    # 日志目录
    if not os.path.exists('/var/log'):
        os.makedirs('/var/log')

    os.chdir('/var/log')

    os.umask(0)

def log(* args):
    '''
        写日志，函数的格式和print()一样
        '''
    global log_file
    
    t = time.localtime(time.time())
    arr = traceback.extract_stack()
    frame = arr[len(arr) - 2]
    msg = "%d-%d-%d %d:%d:%d %s (%d) %s()"%(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec,frame[0],frame[1],frame[2])
    for i in args:
        msg += ' ' + str(i)
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

def has_ip(ip):
    '''
        判断本机地址是否有某个ip
    '''
    dic = psutil.net_if_addrs()
    for adapter in dic:
        snicList = dic[adapter]
        for snic in snicList:
            if snic.address == ip:
                return True
    return False

def main():
    global log_file
    global app_path
    global IP
    
    if sys.argv[0][0] == '.' and sys.argv[0][1] == '/':
        app_path = os.getcwd() + '/' + sys.argv[0][2:]
    else:
        app_path = os.getcwd() + '/' + sys.argv[0]

    app_path = app_path[0:app_path.rfind('/') + 1]

    try:
        opts,args = getopt.getopt(sys.argv[1:],"dh")
    except getopt.GetoptError:
        print('参数错误')
        return 1

    for opt,value in opts :
        if opt == '-d':
            set_daemonize()
        elif opt == '-h':
            print('./lock_screen.py -h')
            return
    
    log_file = open('lock_screen.log','a')
    log('程序启动...')

    while not has_ip(IP):
        time.sleep(10)

    # 如果没有这个命令需要安装一下，apt install vbetool
    os.system('vbetool dpms off')

    log('启动正常，程序退出')
    log_file.close()

if __name__ == "__main__":
    main()
