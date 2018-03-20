#! /usr/bin/env python
#coding=utf-8

import sqlite3

class SvrDb():
    def __init__(self, path):
        pass
        #sqlite3.__doc__
        #SQLite objects created in a thread can only be used in that same thread.
        self.conn = sqlite3.connect(path, check_same_thread = False)
        sql = 'CREATE TABLE if not exists client(' \
              'c_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
              'c_cid VARCHAR(260) UNIQUE,' \
              'c_ver VARCHAR(260),' \
              'c_localip VARCHAR(20),' \
              'c_remoteip VARCHAR(20),' \
              'c_username VARCHAR(260),' \
              'c_osver VARCHAR(260),' \
              'c_firsttime DATETIME,' \
              'c_lasttime DATETIME,' \
              'c_status INT' \
              ' );'
        sql1 = 'CREATE TABLE if not exists task(' \
              't_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
              't_cid VARCHAR(260),' \
              't_task VARCHAR(260),' \
              't_argv VARCHAR(4096),' \
              't_time DATETIME' \
              ' );'
        try:
            self.conn.execute(sql)
            self.conn.execute(sql1)
            self.conn.commit()
        except Exception as e:
            print '<__init__>', e

    #id = computer_name_time
    def add_client(self, id, ver, info):
        if self.get_client(id):
            self.upd_client(id, 
                            ver, 
                            lip=info['lip'], 
                            rip=info['rip'],
                            uname=info['uname'],
                            osv=info['osver'],
                            status=1)
            #print '<add_client> already exist'
            return

        sql = "insert into client(" \
              "c_cid, c_ver, c_localip, c_remoteip, " \
              "c_username, c_osver, c_firsttime," \
              "c_lasttime, c_status)" \
              "values ('%s', '%s', '%s', '%s', '%s', '%s', datetime(\"now\", \"localtime\"), datetime(\"now\", \"localtime\"), %d)"
        sql = sql % (id, ver, info['lip'], info['rip'], info['uname'], info['osver'], 1)
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<add_client>', e
    
    def get_client(self, id):
        sql = "select * from client where c_cid = '%s'" % id
        try:
            cursor = self.conn.execute(sql)
            if cursor:
                return cursor.fetchall()
        except Exception as e:
            print e
        return None
    
    def list_client(self):
        sql = "select * from client;"
        try:
            cursor = self.conn.execute(sql)
            if cursor:
                return cursor.fetchall()
        except Exception as e:
            print e
        return None

    def list_alive_client(self):
        sql = "select * from client where c_status=1;"
        try:
            cursor = self.conn.execute(sql)
            if cursor:
                return cursor.fetchall()
        except Exception as e:
            print e
        return None

    def del_client(self, id):
        sql = "delete from client where c_cid='%s'" % id
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<del_client>', e
    
    def del_all_client(self):
        sql = 'delete from client;'
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<del_all_client>', e

    def upd_client(self, id, ver='', lip='', rip='', uname='', osv='', status=-1):
        sql = 'update client set '
        sql += (('c_ver=\'%s\',' % ver) if ver else '')
        sql += (('c_localip=\'%s\',' % lip) if lip else '')
        sql += (('c_remoteip=\'%s\',' % rip) if rip else '')
        sql += (('c_username=\'%s\',' % uname) if uname else '')
        sql += (('c_osver=\'%s\',' % osv) if osv else '')
        sql += (('c_status=%d,' % status) if status!=-1 else '')
        sql += ('c_lasttime=datetime("now", "localtime"),')
        sql = sql[:-1] + (' where c_cid=\'%s\'' % id)
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<upd_client>', e

    def off_client(self, id):
        sql = 'update client set c_status = 0'
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<off_client>', e
        
    def close(self):
        self.conn.close()

    def add_task(self, id, task, argv=''):
        if not self.get_client(id):
            print '<add_task> %s is not exist' % id
            return
        sql = "insert into task(t_cid, t_task, t_argv, t_time) VALUES ('%s', '%s', '%s', datetime('now', 'localtime'));"
        sql = sql % (id, task, argv)
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<add_task>', e

    def get_task(self, id):
        sql = "select * from task where t_cid='%s' limit 1;" % id
        try:
            cursor = self.conn.execute(sql)
            return cursor.fetchone()
        except Exception as e:
            print '<get_task>', e
        return None
    
    def del_task(self, tid):
        sql = "delete from task where t_id=%d" % tid
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<del_task>', e

    def clean_task(self, id):
        sql = "delete from task where t_cid='%s'" % id
        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print '<clean_task>', e
        
if __name__ == '__main__':
    sd = SvrDb("svr.db")

    '''
    id = 'myhost_1520264904.385'
    ver = '1.0'
    info = {
        'lip':'192.168.0.100',
        'rip':'61.11.12.90',
        'uname':'myhost',
        'osver':'win10'
    }
    sd.add_client(id, ver, info)
    sd.add_client(id, ver, info)
    sd.upd_client(id, ver='1.2', lip='192.168.0.101', rip='111.111.111.111', uname='myhost2', status=1)
    #sd.del_client(id)

    sd.add_task(id, "update", "v=1.3")
    print sd.get_task(id)
    tid=raw_input("tid >")
    sd.del_task(int(tid))
    '''

    c = sd.list_alive_client()
    for i in c:
        print i
    sd.close()
