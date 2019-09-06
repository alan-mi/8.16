# coding:utf-8
import multiprocessing

from cluster_raft import tools
from cluster_raft.raft_obj import DCSyncObj
from cluster_raft.tools import local_ip

raft_port = '8585'
selfNode = local_ip() + ":" + raft_port
tools.raft_loop.set()
allNode = ["192.168.137.2:8585", "192.168.137.3:8585", "192.168.137.4:8585"]

raft_obj = DCSyncObj(selfNode, allNode)
