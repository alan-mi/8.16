# coding:utf-8
import ctypes
import inspect
import logging
import os
from logging import handlers
from socket import socket, AF_INET, SOCK_STREAM
from multiprocessing import Event
from threading import Thread

vip_event = Event()
raft_loop = Event()
up_event = Event()

log_dir = os.path.expanduser('/tmp') + '/raft'
log_name = 'raft'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
elif not os.path.isdir(log_dir):
    os.makedirs(log_dir)
else:
    pass

logger = logging.getLogger(log_name)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(pathname)s %(funcName)s [line:%(lineno)d] %(threadName)s %(message)s')

logfile = handlers.TimedRotatingFileHandler(
    filename='{}/{}.log'.format(log_dir, log_name),
    # 大小写不敏感 s/m/h/d/S/M/H/D
    when='d',
    # 间隔
    interval=1,
    # 日志保存个数
    backupCount=10
)
# logfile.setLevel(logging.CRITICAL)
# logfile.setLevel(logging.ERROR)
logfile.setLevel(logging.WARNING)
# logfile.setLevel(logging.INFO)
# logfile.setLevel(logging.DEBUG)
logfile.setFormatter(formatter)
logger.addHandler(logfile)

console = logging.StreamHandler()
# console.setLevel(logging.CRITICAL)
# console.setLevel(logging.ERROR)
# console.setLevel(logging.WARNING)
# console.setLevel(logging.INFO)
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)


def local_ip():
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(("1.1.1.1", 80))
    ip = s.getsockname()[0]
    logger.info("当前IP{}".format(ip))
    return ip


def Singleton(func):
    ins = {}

    def _wraper(self, *args, **kwargs):
        if func not in ins:
            ins[func] = func(self, *args, **kwargs)
        return ins[func]
    return _wraper


def get_all_nodes_from_raft_status(i: dict) -> dict:
    nodes = {}
    for k in i.keys():
        # 获取本机的ip地址 及端口号
        if k == 'self':
            # 把本机放入 nodes中 设置状态为2
            nodes[i[k]] = 2
        if k.startswith('partner_node_status_server_'):
            nodes[k[27:]] = i[k]
    return nodes


def stop_thread(thread, exctype=SystemExit):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(thread.ident)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    logger.info("杀死线程结果{}".format(res))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def spawn(**kwargs):
    t = Thread(**kwargs)
    t.daemon = True
    t.start()
    return t
