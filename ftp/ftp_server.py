'''
ftp 文件服务器
'''
from socket import *
import os,sys
import time
import signal
#文件库路径
FILE_PATH = '/home/tarena/ftpfile/'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)

#将文件服务器功能写在类中
class FtpServer(object):
    def __init__(self,c):
        self.c = c
    def do_list(self):
        #获取文件列表
        file_list = os.listdir(FILE_PATH)
        if not file_list:
            self.c.send("文件库为空".encode())
            return
        else:
            self.c.send(b"OK")
            time.sleep(0.1)
        files = ''
        for file in file_list:
            if file[0] != '.' and os.path.isfile(FILE_PATH + file):
                files = files + file + '#'
        self.c.sendall(files.encode())
    def do_get(self,filename):
        try:
            f = open(FILE_PATH+filename,'rb')
        except:
            self.c.send(b"fail")
        self.c.send(b'OK')
        time.sleep(0.1)
        while True:
            data = f.read(1024)
            if not data:
                time.sleep(0.1)
                self.c.send(b'##')
                f.close()
                break
            self.c.send(data)
        print("文件发送完毕")
    def do_put(self,filename):
        try:
            fd = open(FILE_PATH+filename,'wb')
        except:
            self.c.send(b"fail")
        self.c.send(b'OK')
        time.sleep(0.1)
        while True:
            data = self.c.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()
        print("%s 上传完毕\n"%filename)



#创建套接字，接受客户端连接，创建新的进程
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen()

    #在父进程中忽略子进程状态改变，子进程退出自动由系统处理
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    print("Listen the port 8888...")
    while True:
        try:
            c,addr = s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("服务器异常:",e)
            continue
        print("已连接客户端：",addr)
        #为客户端创建新的进程处理请求
        pid = os.fork()
        #子进程处理具体请求
        if pid == 0:
            s.close()
            ftp = FtpServer(c)
            while True:
                #判断客户端请求
                data = c.recv(1024).decode()
                if not data or data[0] == 'q':
                    c.close()
                    sys.exit("客户端退出")
                elif data[0] == "1":
                    ftp.do_list()
                elif data[0] == '2':
                    filename = data.split(' ')[1]
                    ftp.do_get(filename)
                elif data[0] == '3':
                    filename = data.split(' ')[-1]
                    ftp.do_put(filename)
        #父进程或者创建失败都继续等待下个客户端连接
        else:
            c.close()
            continue


if __name__ == '__main__':
    main()



