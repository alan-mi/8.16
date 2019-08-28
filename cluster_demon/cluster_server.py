# coding:utf-8
import json
import time
from concurrent import futures

import grpc

from cluster_demon.proto import sch_pb2, sch_pb2_grpc
from cluster_demon.utils.tools import get_node_gpu_count
from cluster_demon.utils.client_mongo import cli

class ClusterGRPCServer(sch_pb2_grpc.SkylarkServicer):
    def HeartBeat(self, request, complext):
        version = request.version
        seq = request.seq
        timestamp = request.timestamp
        body = request.body
        a = {'machineID': '_001|_020', 'callbackAddress': '113.204.194.92:1320', 'clusterID': '_003', 'gpus': [{'model': 'GeForce GTX 1080 Ti', 'count': 1}, {'model': 'GeForce GTX 1070 Ti', 'count': 2}], 'Status': 2}
        body = json.loads(body)
        body.update({"heartBeat":int(time.time())})
        cli.insert_update(body)
        err = {"msg":"ok","status":2}
        return sch_pb2.Proto(version = version,seq = seq,timestamp = int(time.time()),body =json.dumps(err).encode())


    def TaskStatus(self, request, context):
        version = request.version
        seq = request.seq
        timestamp = request.timestamp
        body = request.body
        body = json.loads(body)
        err = {}
        proj_fields_map = {
            "taskID": "mi_alan",
            "taskType": 3,
            "taskName": "task_name",
            "projectHash": "QmPhoTxquhjH14hb5S82jnDtu8FcLnGzNZEvgN1jCtN15P",
            "gpus": [{"model": "GeForce GTX 1080 Ti", "count": 4}, {"model": "GeForce GTX 1070 Ti", "count": 0}],
            "engine": 2,
            "mainRelativePath": "pytorch_demo/demo_s_d/torch_mnist_demo.py",
            "runParam": "",
            "projectName": "pytorch_demo.zip",
            "outputPath": "pytorch_demo/demo_s_d/out"
        }
        if body["taskType"] == "start":
            gpus = proj_fields_map["gpus"]
            if cli.compare_gpu(gpus):
                task = cli.chooice_use_gpu_by_num(gpus,task_id=proj_fields_map["taskID"])
                print(task)
                for mac,gpu in task["machines"].items():
                    print(mac)
                    print(gpu)
                err = {"msg": "ok", "status": 2}
            else:
                err = {"msg": "gpu_not_free", "status": 1}
                cli.free_gpu_by_task_id(proj_fields_map["taskID"])
        if body["taskType"] == "start":
            pass
        return sch_pb2.Proto(version=version, seq=seq, timestamp=int(time.time()), body=json.dumps(err).encode())















class ClusterServer(object):

    def __init__(self, addr, max_workers=40):
        self.addr = addr
        self.max_workers = max_workers
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        self.service = ClusterGRPCServer()

    def start(self):
        try:
            sch_pb2_grpc.add_SkylarkServicer_to_server(self.service,self.server)
            self.server.add_insecure_port('{}'.format(self.addr))
            self.server.start()

            # while True:
            #     time.sleep(60*60*24)

        except KeyboardInterrupt:
            self.server.stop(0)

    def stop(self):
        self.server.stop(0)



if __name__ == '__main__':
    cs = ClusterServer(addr = "0.0.0.0:8400")
    cs.start()
