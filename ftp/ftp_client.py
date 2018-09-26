'''
ftp 文件客户端
'''
from socket import *
from menu import show_menu
import sys
import time

#基本文件操作功能
class FtpClient(object):
    def __init__(self,s):
        self.s = s
    def do_list(self):
        self.s.send(b'1')  #发送请求
        data = self.s.recv(1024).decode()
        if data == 'OK':
            data = self.s.recv(4096).decode()
            files = data.split('#')
            for file in files:
                print(file)
            print("文件列表展示完毕\n")
        else:
            #由服务器发送失败原因
            print(data)
    def do_get(self):
        filename = input("请输入要下载的文件名：")
        self.s.send(b'2 ' + filename.encode())
        data = self.s.recv(1024).decode()
        if data == 'OK':
            data = self.s.recv(4096).decode()
            fd = open(filename,'wb')
            while True:
                data = self.s.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
            print("%s 下载完毕\n"%filename)
        else:
            print(data)
    def do_quit(self):
        self.s.send(b'q')
    def do_put(self):
        path = input("请输入要上传的文件目录：")
        filename = input("请输入要上传的文件名：")
        self.s.send(b'3 ' + filename.encode())
        data = self.s.recv(1024).decode()
        if data == 'OK':
            try:
                f = open(path+filename,'rb')
            except:
                self.s.send("文件不存在".encode())
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.s.send(b'##')
                    f.close()
                    break
                self.s.send(data)
            print("文件上传成功")
        else:
            print(data)

#网络连接
def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST,PORT)
    s = socket()
    try:
        s.connect(ADDR)
    except :
        print("连接服务器失败")
        return
    ftp = FtpClient(s)#功能类对象
    while True:
        show_menu()
        cmd = input("请选择:")
        if not cmd :
            break
        elif cmd.strip() == '1':
            ftp.do_list()
        elif cmd.strip() == '2':
            ftp.do_get()
        elif cmd.strip() == '3':
            ftp.do_put()
        elif cmd.strip() == 'q':
            ftp.do_quit()
            s.close()
            sys.exit("谢谢使用")
if __name__ == '__main__':
    main()
