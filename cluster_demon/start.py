# coding:utf-8
import json
import time
from threading import Thread

import grpc
import requests

from cluster_demon.utils.dc_vip import vip
from cluster_raft import raft_grpc_pb2_grpc, raft_grpc_pb2
from cluster_raft.raft_main import main
# 启动raft
from cluster_raft.tools import vip_event, local_ip, spawn
from multiprocessing import Process
def run():
    for i in range(1000):
        time.sleep(1)
        req = requests.get(" http://192.168.137.200:8586/status")
        print(req.json())

if __name__ == '__main__':
    spawn(target = run)
    main()




