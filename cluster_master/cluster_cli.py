# coding:utf-8
import hashlib
import json
import random
import time

import grpc

from cluster_master.proto import sch_pb2_grpc, sch_pb2

import time

from cluster_master.utils.client_mongo import cli
from conf import CONFIG


def test_rpc_heart():
    try:
        with grpc.insecure_channel("192.168.137.200:{}".format(CONFIG.get("master_port"))) as channel:
            stub = sch_pb2_grpc.SkylarkStub(channel=channel)
            # time.sleep(3)
            a = {"machineID": "_001|_{:03}".format(random.randint(0, 1000)),
                 "clusterID": "_003",
                 "ctrlAvailable": "N",
                 "taskType": "start",
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
                     }],
                 "callbackAddress": "61.142.213.210:22004",
                 "intranetAddress": "192.168.137.4:28801",
                 "geoCode": "0757-1",
                 "status": 2,
                 }
            res = stub.HeartBeat(
                sch_pb2.Proto(
                    version=1,
                    seq=1,
                    timestamp=int(
                        time.time()),
                    body=json.dumps(a).encode()),
                timeout=5)
            print(json.loads(res.body))
    except Exception as e:
        print("error", e)


def test_rpc_task():
    try:
        with grpc.insecure_channel("192.168.137.200:{}".format(CONFIG.get("master_port"))) as channel:
            stub = sch_pb2_grpc.SkylarkStub(channel=channel)
            # time.sleep(3)
            status = random.choice(["start", "stop"])
            id = hashlib.md5(bytes(random.randint(0, 1000))).hexdigest()
            print(id)
            proj_fields_map = {
                "taskID": "{}".format(id),
                "taskType": 3,
                "taskName": "task_name",
                "projectHash": "QmPhoTxquhjH14hb5S82jnDtu8FcLnGzNZEvgN1jCtN15P",
                "gpus": random.choices([{"model": "GeForce GTX 1080 Ti", "count": 1},
                                        {"model": "GeForce GTX 1070 Ti", "count": 1}]),
                "engine": 2,
                "mainRelativePath": "pytorch_demo/demo_s_d/torch_mnist_demo.py",
                "runParam": "",
                "projectName": "pytorch_demo.zip",
                "outputPath": "pytorch_demo/demo_s_d/out",
                "status": "stop"
            }
            res = stub.TaskStatus(
                sch_pb2.Proto(
                    version=1,
                    seq=1,
                    timestamp=int(
                        time.time()),
                    body=json.dumps(proj_fields_map).encode()),
                timeout=5)
            print(json.loads(res.body))
    except Exception as e:
        print("error", e)


if __name__ == '__main__':
    i = 0
    while True:
        test_rpc_heart()
        i += 1
        print("织女星", i)
        test_rpc_task()
