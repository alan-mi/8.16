import grpc
from protocol import cluster_strategy_pb2_grpc

from cluster_monitor.utils import common

channel = grpc.insecure_channel(
    common.CLUSTER_CONF.get('cluster_lv1_call_center'))
stub = cluster_strategy_pb2_grpc.StrategyServiceStub(channel)
