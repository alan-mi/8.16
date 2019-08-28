# coding:utf-8
import sys
import time

from cluster_raft.raft_init import raft_obj
from cluster_raft.raft_main import main
from cluster_raft.tools import local_ip
from multiprocessing import Process,Event
raft_port = '8585'
selfNode = local_ip()+":"+raft_port

slave_status = Event()
cluster_status = Event()
task = {'machineID': '_001|_020', 'callbackAddress': '113.204.194.92:1320', 'clusterID': '_003', 'gpus': [{'model': 'GeForce GTX 1080 Ti', 'count': 1}, {'model': 'GeForce GTX 1070 Ti', 'count': 2}], 'Status': 2}






if __name__ == '__main__':
    print(raft_obj.getStatus())
    main()
    if not raft_obj.getStatus().get("leader"):
        while True:
            time.sleep(2)
            print(raft_obj.getStatus())
            if raft_obj.getStatus().get("leader"):
                print("本机IP",raft_obj.selfNodeAddr)
                print("集群IP",raft_obj.allNodeAddrs)
                raft_obj.setcounter()
                print("计数器",raft_obj.getcounter())
                # #
                # while "192.168.137.3:8585" in raft_obj.allNodeAddrs:
                #     time.sleep(2)
                #     if raft_obj.getStatus()["leader"] == "192.168.137.3:8585":
                #         break
                #     raft_obj.removeNodeFromClusterDC("192.168.137.3:8585")
                #     print("还没删除")
                #     continue
                # print("删除后集群IP", raft_obj.allNodeAddrs)
                # print("删除后集群状态",raft_obj.getStatus())

                # while "192.168.137.3:8585" not in raft_obj.allNodeAddrs:
                #     raft_obj.addNodeToClusterDC("192.168.137.3:8585")
                #     time.sleep(2)
                #     print("添加不成功")
                #     continue
                # if raft_obj.getcounter() ==250:
                #     raft_obj.dc_election()
                raft_obj.addNodeToClusterDC(selfNode)
                print("添加后集群IP", raft_obj.allNodeAddrs)
                print("添加后集群状态", raft_obj.getStatus())
                # raft_obj.dc_election()
            if raft_obj.getStatus().get("leader") == selfNode:
                print(raft_obj.getStatus())
                time.sleep(4)
                # raft_obj.dc_election()

        #开启服务
        # import socket
        # s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # s.bind(("0.0.0.0",80))
        # s.listen(5)
        # conn, address = s.accept()
        # mess = b""
        # while True:
        #     data = conn.recv(1024)
        #     if  not data:
        #         break
        #     mess += data



