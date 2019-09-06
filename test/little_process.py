# coding:utf-8
from multiprocessing import Process
import socket
import time


def _bind():
    s = socket.socket()
    s.bind(("", 8888))
    s.listen(5)
    print("监听8888...")
    while True:
        sock, addr = s.accept()
        sock.send(b"hello")


def test(p):

    while True:
        print("test")
        time.sleep(2)
        if not p.is_alive():
            p = Process(target=_bind)
            p.daemon = True
            p.start()


if __name__ == '__main__':
    p = Process(target=_bind)
    p.daemon = True
    p.start()
    test(p)
