# coding:utf-8
import time
from concurrent import futures

import grpc

from cluster_demon.proto import sch_pb2, sch_pb2_grpc
from cluster_demon.utils.tools import get_node_gpu_count


class ClusterGRPCServer(sch_pb2_grpc.SkylarkServicer):
    gpu_merchin = {}
    def HeartBeat(self, request, complext):
        version = request.version
        seq = request.seq
        timestamp = request.timestamp
        body = request.body.decode()
        a = {'machineID': '_001|_020', 'callbackAddress': '113.204.194.92:1320', 'clusterID': '_003', 'gpus': [{'model': 'GeForce GTX 1080 Ti', 'count': 1}, {'model': 'GeForce GTX 1070 Ti', 'count': 2}], 'Status': 2}
        merchin = {body["machineID"]:get_node_gpu_count(body)}
        self.gpu_merchin.update(merchin)









class ClusterServer(object):

    def __init__(self, addr, max_workers=40):
        self.addr = addr
        self.max_workers = max_workers
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        self.service = ClusterGRPCServer()

    def start(self):
        sch_pb2_grpc.add_SkylarkServicer_to_server(self.service,self.server)
        self.server.add_insecure_port('{}'.format(self.addr))
        self.server.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.server.stop(0)

    def stop(self):
        self.server.stop(0)
