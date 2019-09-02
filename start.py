# coding:utf-8
import json
import time
from threading import Thread

import grpc
import requests

from cluster_demon.utils.dc_vip import vip
from cluster_raft import raft_grpc_pb2_grpc, raft_grpc_pb2
from cluster_raft.raft_main import run_server
# 启动raft
from cluster_raft.tools import vip_event, local_ip, spawn
from multiprocessing import Process

if __name__ == '__main__':
    # spawn(target = run)
    run_server()




