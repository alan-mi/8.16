# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from cluster_raft import raft_grpc_pb2 as cluster__raft_dot_raft__grpc__pb2


class RaftServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetStatus = channel.unary_unary(
        '/raft.RaftService/GetStatus',
        request_serializer=cluster__raft_dot_raft__grpc__pb2.GetStatusReq.SerializeToString,
        response_deserializer=cluster__raft_dot_raft__grpc__pb2.GetStatusRes.FromString,
        )
    self.IsRegistered = channel.unary_unary(
        '/raft.RaftService/IsRegistered',
        request_serializer=cluster__raft_dot_raft__grpc__pb2.IsRegisteredReq.SerializeToString,
        response_deserializer=cluster__raft_dot_raft__grpc__pb2.IsRegisteredRes.FromString,
        )


class RaftServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetStatus(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def IsRegistered(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RaftServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetStatus': grpc.unary_unary_rpc_method_handler(
          servicer.GetStatus,
          request_deserializer=cluster__raft_dot_raft__grpc__pb2.GetStatusReq.FromString,
          response_serializer=cluster__raft_dot_raft__grpc__pb2.GetStatusRes.SerializeToString,
      ),
      'IsRegistered': grpc.unary_unary_rpc_method_handler(
          servicer.IsRegistered,
          request_deserializer=cluster__raft_dot_raft__grpc__pb2.IsRegisteredReq.FromString,
          response_serializer=cluster__raft_dot_raft__grpc__pb2.IsRegisteredRes.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'raft.RaftService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))