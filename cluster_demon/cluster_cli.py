# coding:utf-8
import json
import time

import grpc

from cluster_demon.proto import sch_pb2_grpc, sch_pb2

import time
def test_rpc():
    while True:
        time.sleep(3)
        try:

            with grpc.insecure_channel("192.168.137.200:8300") as channel:
                stub = sch_pb2_grpc.SkylarkStub(channel=channel)
                # time.sleep(3)
                a = {"machineID": "_001|_020",
                     "clusterID": "_003",
                     "ctrlAvailable": "N",
                     "taskType" :"start",
                     "gpus": [
                         {
                             "model": "GeForce GTX 1070 Ti",
                             "id": 1,
                             "status": None
                         },
                         {
                             "model": "GeForce GTX 1080 Ti",
                             "id": 0,
                             "status": None
                         },
                         {
                             "model": "GeForce GTX 1080 Ti",
                             "id": 1,
                             "status": None
                         }]
                     }
                res = stub.HeartBeat(sch_pb2.Proto(version=1, seq=1, timestamp=int(time.time()), body=json.dumps(a).encode()),
                                     timeout=5)
                print(json.loads(res.body))
        except Exception as e:
            print("error",e)
            continue

if __name__ == '__main__':
    test_rpc()





