#! /usr/bin/env python
#coding=utf-8

import sys, subprocess
import os, uuid
import platform
import ctypes
import win32api, win32com, win32gui, win32ui

def GetClientId():
    name = win32api.GetUserName()
    mac = uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
    return name + '-' + mac

def GetLocalIp():
    import socket
    return socket.gethostbyname(socket.gethostname())

def GetPublicIp():
    #http://www.jb51.net/article/57997.htm
    import re,urllib2
    def visit(url):
        opener = urllib2.urlopen(url)
        if url == opener.geturl():
            s = opener.read()
            return re.search('\d+\.\d+\.\d+\.\d+', s).group(0)
        return ''
    try:
        ip = visit("http://2017.ip138.com/ic.asp")
    except:
        try:
            ip = visit("http://m.tool.chinaz.com/ipsel")
        except:
            ip = "unknown"
    return ip

def GetOsVersion():
    uname = list(platform.uname())
    #print sys.platform, uname
    return str(uname[0]) + str(uname[3])

def GetClientInfo():
    info = {
        "uname": win32api.GetUserName(),
        "osver": GetOsVersion(),
        "lip": GetLocalIp(),
        "rip": GetPublicIp(),
    }
    return info

if __name__ == '__main__':
    print GetClientId()
    print GetClientInfo()
