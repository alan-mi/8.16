# coding:utf-8
import grpc
import time
import json

from cluster_demon.utils.dc_vip import vip
from cluster_raft import (
    raft_grpc_pb2,
    raft_grpc_pb2_grpc
)
from cluster_raft.tools import local_ip, vip_event

if __name__ == '__main__':
    # with grpc.insecure_channel(local_ip()+':8200') as chan:
    #     stub = raft_grpc_pb2_grpc.RaftServiceStub(channel=chan)
    #     while True:
    #         time.sleep(1)
    #         ts = int(time.time())
    #         res_f = stub.GetStatus.future(raft_grpc_pb2.GetStatusReq(ts=str(ts)))
    #         if res_f.result().ts == str(ts):
    #             print(json.loads(res_f.result().status))
    vip_event.set()
    try:
        with grpc.insecure_channel(local_ip() + ':8200') as chan:
            stub = raft_grpc_pb2_grpc.RaftServiceStub(channel=chan)
            while True:
                time.sleep(1)
                ts = int(time.time())
                try:
                    res_f = stub.GetStatus.future(
                        raft_grpc_pb2.GetStatusReq(ts=str(ts)))
                    if res_f.result().ts == str(ts):
                        raft_status = json.loads(res_f.result().status)
                        print(
                            vip_event.is_set(),
                            raft_status['leader'],
                            raft_status['self'],
                            raft_status["state"])
                        if vip_event.is_set(
                        ) and raft_status['leader'] == raft_status['self'] and raft_status["state"] == 2:
                            vip.set_vip("up")
                            vip_event.clear()
                        if not vip_event.is_set(
                        ) and raft_status['leader'] != raft_status['self']:
                            vip.set_vip("down")
                            vip_event.set()
                except Exception as e:
                    print(e)
                    continue
    except KeyboardInterrupt:
        vip.set_vip("down")
        exit("退出")
