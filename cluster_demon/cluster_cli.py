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
                proj_fields_map = {
                    "taskID": "mi_alan",
                    "taskType": 3,
                    "taskName": "task_name",
                    "projectHash": "QmPhoTxquhjH14hb5S82jnDtu8FcLnGzNZEvgN1jCtN15P",
                    "gpus": [{"model": "GeForce GTX 1080 Ti", "count": 2},
                             {"model": "GeForce GTX 1070 Ti", "count": 1}],
                    "engine": 2,
                    "mainRelativePath": "pytorch_demo/demo_s_d/torch_mnist_demo.py",
                    "runParam": "",
                    "projectName": "pytorch_demo.zip",
                    "outputPath": "pytorch_demo/demo_s_d/out",
                    "status": "stop"
                }
                res = stub.TaskStatus(sch_pb2.Proto(version=1, seq=1, timestamp=int(time.time()), body=json.dumps(proj_fields_map).encode()),
                                     timeout=5)
                print(json.loads(res.body))
        except Exception as e:
            print("error",e)
            continue

if __name__ == '__main__':
    test_rpc()





