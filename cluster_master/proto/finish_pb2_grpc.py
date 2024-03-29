# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from protocol import finish_pb2 as finish__pb2


class ComputedStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.finish = channel.unary_unary(
            '/cluster.Computed/finish',
            request_serializer=finish__pb2.Req.SerializeToString,
            response_deserializer=finish__pb2.Res.FromString,
        )


class ComputedServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def finish(self, request, context):
        # missing associated documentation comment in .proto file
        pass
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ComputedServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'finish': grpc.unary_unary_rpc_method_handler(
            servicer.finish,
            request_deserializer=finish__pb2.Req.FromString,
            response_serializer=finish__pb2.Res.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'cluster.Computed', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
