# PyRat

PyRat，基于python XmlRPC完成的远控开源项目，包括客户端和服务端（也叫控制端，后统称服务端）。

> 申明：项目仅供技术交流，请勿用于商业及非法用途，如产生任何法律纠纷均与本人无关!

1. 由于XmlRPC基于http协议，所以PyRat能够无视防火墙，更加优雅得进行通信和控制。
2. python的跨平台特性，使得PyRat客户端可以支持Windows/Linux/Macos等不同平台，目前测试通过支持**Windows/Ubuntu/Macos**平台。
3. 服务端命令行控制和管理，逼格满满。
4. 目前客户端支持基本信息、上传、下载、cmdshell、运行软件、结束进程、更新、卸载等功能

# 依赖

1. python2.7
2. colorama (服务端)

# TODO

1. 增加更多功能，比如文件操作，批量断点文件传输，远程桌面，截屏，账户操作等等
2. 服务端可视化
3. 交互式shell
4. 加密隧道
5. SSH / SCP
6. 欢迎PR

# 基本使用

客户端

```
> python .\pyratcli.py localhost 80
```

服务端

```
> python pyratsvr.py 80
--------------------Python RAT-----------------------
--------------------anhkgg---------------------------
--------------------Copyright (c) 2018---------------

软件仅供技术交流，请勿用于商业及非法用途，如产生法律纠纷与本人无关!

--------------------Task command---------------------
--|(l)ist (a)live (k)ill (s)elect (p)rint (c)mdshell (n)ew (d)ownload (r)unexec (u)pload (t)erminate (q)uit (h)elp|--

cmd >
```

客户端上线后，服务端会提示，并且将最新上线客户端设置未默认操作目标。

```
cmd >test-3333333 is online.
Auto set target test-3333333
```

`help`或者`h`可列出服务端支持的所有命令。

```
cmd >help
(l)ist:     list all clients
(a)live:    list alive clients
(k)ill:     delete client
(s)elect:   select target client
(p)rint:    show current client
(c)mdshell: create a cmdshell, type q to exit cmdshell
(n)ew:      update client version
(d)ownload: let client download a file
(r)unexec:  let client run a exe
(u)pload:   upload a file to client
(t)erminate:terminate process
(q)uit:     quit server
```

# 客户端管理

服务端使用sqlite保存客户端基础信息以及任务信息，通过命令可以对客户端进行管理。

```
//枚举所有客户端
cmd >l
test-3333333 offline 2018-03-20 22:46:59!
id     | client_id                  | version  | localip              | remoteip             | username             | osversion  | firsttime            | lasttime             | status
10     | test-3333333     | 0.1.0    | 192.168.149.1        | 114.245.47.12        | test            | Windows10.0.16299 | 2018-03-17 12:39:56  | 2018-03-20 22:46:59  | 0
cmd >
//枚举在线客户端
cmd >a
no alive client
//删除客户端数据库记录或者卸载客户端
cmd >k
target cid(or ALL):test-3333333
Do you want to uninstall client?(Y/N)
```

如果需要控制客户端时，需要通过`select`或者`s`选择要操作的客户目标。

```
cmd >c //想进入cmdshell，提示无目标
Please first set target client by (s)elect command.
cmd >s //设置目标
client_id:test-3333333
Set target client: test-3333333
//查看当前目标
cmd >p
test-3333333
```

# cmdshell

通过`cmdshell`或`c`进入cmdshell，除非主动输入`q`，否则一直在cmdshell操作目录。

cmdshell记录操作目录，比如cd c:\，下次操作会在该目录下进行，实现了类似管道连接的cmdshell。

另外若通过cmdshell启动进程，某些进程可能会阻塞消息返回，所以不推荐使用，而是使用`runexec`来代替。

```
cmd >c
RAT-CMD > dir
RAT-CMD > test-3333333 do cmdshell(195) dir True
 驱动器 D 中的卷是 gitrepo
 卷的序列号是 EB2F-5AC0

 D:\PyRat\client 的目录

2018/02/24  09:40    <DIR>          .
2018/02/24  09:40    <DIR>          ..
2018/03/20  22:46             4,919 pyratcli.py
2018/03/20  23:01                28 cmd.log
2018/03/17  12:39             1,322 pyratfc.py
2018/03/17  11:19             2,500 osver.py
2018/03/17  12:39             2,161 pyratfc.pyc
               5 个文件         10,930 字节
               2 个目录 647,836,565,504 可用字节

RAT-CMD > ver
RAT-CMD > test-3333333 do cmdshell(196) ver True

Microsoft Windows [版本 10.0.16299.309]

RAT-CMD > tasklist
RAT-CMD > test-3333333 do cmdshell(197) tasklist True

映像名称                       PID 会话名              会话#       内存使用
========================= ======== ================ =========== ============
System Idle Process              0 Services                   0          8 K
System                           4 Services                   0      3,564 K
smss.exe                       360 Services                   0        412 K
csrss.exe                      492 Services                   0      1,700 K
Calculator.exe               21656 RDP-Tcp#85                 1     56,772 K
RAT-CMD > tasklist |findstr Cal
RAT-CMD > test-3333333 do cmdshell(200) tasklist |findstr Cal True
Calculator.exe               21656 RDP-Tcp#85                 1     51,856 K
RAT-CMD > taskkill /IM Calculator.exe
RAT-CMD > test-3333333 do cmdshell(201) taskkill /IM Calculator.exe True
成功: 给进程 "Calculator.exe" 发送了终止信号，进程的 PID 为 21656。
RAT-CMD > taskkill /PID 21656
RAT-CMD > test-3333333 do cmdshell(202) taskkill /PID 21656 True
成功: 给进程发送了终止信号，进程的 PID 为 21656。
```

# 文件操作

支持文件上传和下载，其中下载支持下载网络文件和服务端本地文件，暂时只支持单文件上传和下载。

```
cmd >d
url(type N to download local file):N //选择下载本地文件
local file:db.db
dest path:db.db
cmd >test-3333333 do download(203) local db.db db.db True
download success

cmd >d
url(type N to download local file):https://dl.360safe.com/360/inst.exe //下载网络文件
dest path:inst.exe
cmd >test-3333333 do download(204) net https://dl.360safe.com/360/inst.exe inst.exe True
download success
```

# 运行软件

```
cmd >r
run target:inst.exe
runexec inst.exe
```

# 结束进程

```
cmd > t
Select type(name/pid):name
process name:notepad.exe
cmd >test-3333333 do terminate(212) name notepad.exe True
成功: 给进程 "notepad.exe" 发送了终止信号，进程的 PID 为 25416。
```

# 问题

1. 测试中发现可能有编码问题

如果客户端运行在linux，而服务端在windows平台，中文可能出现乱码，因为两个平台使用编码不同，暂时未作处理

# 捐助

![img](wechatpay.png)