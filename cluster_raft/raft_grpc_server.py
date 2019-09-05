# coding:utf-8
import json

from cluster_raft import (
    raft_grpc_pb2,
    raft_grpc_pb2_grpc
)
from cluster_raft import raft_init


class RaftService(raft_grpc_pb2_grpc.RaftServiceServicer):
    def GetStatus(self, request, context):
        ts = request.ts
        # 获取状态 raft 对象状态 并返回
        status = raft_init.raft_obj.getStatus()
        status['isReady'] = raft_init.raft_obj.isReady()
        return raft_grpc_pb2.GetStatusRes(
            ts=ts,
            status=json.dumps(status)
        )
    # 注册

    def IsRegistered(self, request, context):
        from cluster_raft import raft_init
        ts = request.ts
        # 获取注册状态 默认返回False
        status = raft_init.raft_obj.dc_get_registered()
        if request.need_set and status != request.set_status:
            raft_init.raft_obj.dc_set_registered(request.set_status)
            return raft_grpc_pb2.IsRegisteredRes(
                ts=ts,
                changed=status != request.set_status,
                status=status
            )
        else:
            return raft_grpc_pb2.IsRegisteredRes(
                ts=ts,
                status=status
            )
