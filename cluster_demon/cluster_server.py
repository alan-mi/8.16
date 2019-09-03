# coding:utf-8
import json
import time
from concurrent import futures

import grpc

from cluster_demon.proto import sch_pb2, sch_pb2_grpc,agent_pb2,agent_pb2_grpc
from cluster_demon.utils.tools import get_node_gpu_count, sch_response,agent_response
from cluster_demon.utils.client_mongo import cli
from cluster_raft.tools import logger



class ClusterGRPCServer(sch_pb2_grpc.SkylarkServicer):
    def HeartBeat(self, request, complext):
        version = request.version
        seq = request.seq
        timestamp = request.timestamp
        body = request.body
        body = json.loads(body)
        # logger.info("接收到{}心跳".format(body.get("machineID")))
        body.update({"heartBeat":int(time.time())})
        cli.insert_update(body)
        err = {"msg":"ok","status":2}
        return sch_response(err)


    def TaskStatus(self, request, context):
        version = request.version
        seq = request.seq
        timestamp = request.timestamp
        body = request.body
        body = json.loads(body)
        err = {}
        if body["status"] == "start":
            logger.info("任务开始...")
            gpus = body["gpus"]
            if cli.compare_gpu(gpus):
                all_chooice_machine = cli.chooice_use_gpu_by_num(gpus,task_id=body["taskID"])
                print(all_chooice_machine)
                print("GPU发送到任意机器")
                err = {"msg": "ok", "status": 2}
                body.update(all_chooice_machine["machines"])
                try:
                    with grpc.insecure_channel("192.168.137.4:28801") as channel:
                        stub = agent_pb2_grpc.AgentServerStub(channel=channel)
                        stub.TaskStart(agent_response(body))
                except Exception as e:
                    print(e)

            else:
                err = {"msg": "gpu_not_free", "status": 1}


        if body["status"] == "stop":
            logger.info("任务停止...")
            print("根据taskid找出任意机器发送停止任务")


            cli.free_gpu_by_task_id(body["taskID"])


        if body["status"] == "finish":
            logger.info("任务完成...")
            print("根据taskid释放gpu发送完成状态给调度")
            cli.free_gpu_by_task_id(body["taskID"])

        return sch_response(err)















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




        except KeyboardInterrupt:
            self.server.stop(0)

    def stop(self):
        self.server.stop(0)



if __name__ == '__main__':
    cs = ClusterServer(addr = "0.0.0.0:8300")
    cs.start()
    while True:
        time.sleep(60*60*24)
