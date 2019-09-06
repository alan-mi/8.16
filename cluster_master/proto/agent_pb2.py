# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: agent.proto

from google.protobuf import symbol_database as _symbol_database
from google.protobuf import reflection as _reflection
from google.protobuf import message as _message
from google.protobuf import descriptor as _descriptor
import sys
_b = sys.version_info[0] < 3 and (
    lambda x: x) or (
        lambda x: x.encode('latin1'))
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(name='agent.proto', package='tesra', syntax='proto3', serialized_options=_b('\n\rio.grpc.tesraB\nTesraProtoP\001\242\002\003TSP'), serialized_pb=_b(
    '\n\x0b\x61gent.proto\x12\x05tesra\"F\n\x05Proto\x12\x0f\n\x07version\x18\x01 \x01(\x05\x12\x0b\n\x03seq\x18\x02 \x01(\x03\x12\x11\n\ttimestamp\x18\x03 \x01(\x03\x12\x0c\n\x04\x62ody\x18\x04 \x01(\x0c\"\x17\n\x03Req\x12\x10\n\x08req_args\x18\x01 \x01(\t\"\x1a\n\x03Res\x12\x13\n\x0bres_content\x18\x01 \x01(\t2^\n\x0b\x41gentServer\x12\'\n\tTaskStart\x12\x0c.tesra.Proto\x1a\x0c.tesra.Proto\x12&\n\x08TaskStop\x12\x0c.tesra.Proto\x1a\x0c.tesra.ProtoB#\n\rio.grpc.tesraB\nTesraProtoP\x01\xa2\x02\x03TSPb\x06proto3'))


_PROTO = _descriptor.Descriptor(
    name='Proto',
    full_name='tesra.Proto',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='version', full_name='tesra.Proto.version', index=0,
            number=1, type=5, cpp_type=1, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='seq', full_name='tesra.Proto.seq', index=1,
            number=2, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='timestamp', full_name='tesra.Proto.timestamp', index=2,
            number=3, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='body', full_name='tesra.Proto.body', index=3,
            number=4, type=12, cpp_type=9, label=1,
            has_default_value=False, default_value=_b(""),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=22,
    serialized_end=92,
)


_REQ = _descriptor.Descriptor(
    name='Req',
    full_name='tesra.Req',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='req_args', full_name='tesra.Req.req_args', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=94,
    serialized_end=117,
)


_RES = _descriptor.Descriptor(
    name='Res',
    full_name='tesra.Res',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='res_content', full_name='tesra.Res.res_content', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=119,
    serialized_end=145,
)

DESCRIPTOR.message_types_by_name['Proto'] = _PROTO
DESCRIPTOR.message_types_by_name['Req'] = _REQ
DESCRIPTOR.message_types_by_name['Res'] = _RES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Proto = _reflection.GeneratedProtocolMessageType('Proto', (_message.Message,), dict(
    DESCRIPTOR=_PROTO,
    __module__='agent_pb2'
    # @@protoc_insertion_point(class_scope:tesra.Proto)
))
_sym_db.RegisterMessage(Proto)

Req = _reflection.GeneratedProtocolMessageType('Req', (_message.Message,), dict(
    DESCRIPTOR=_REQ,
    __module__='agent_pb2'
    # @@protoc_insertion_point(class_scope:tesra.Req)
))
_sym_db.RegisterMessage(Req)

Res = _reflection.GeneratedProtocolMessageType('Res', (_message.Message,), dict(
    DESCRIPTOR=_RES,
    __module__='agent_pb2'
    # @@protoc_insertion_point(class_scope:tesra.Res)
))
_sym_db.RegisterMessage(Res)


DESCRIPTOR._options = None

_AGENTSERVER = _descriptor.ServiceDescriptor(
    name='AgentServer',
    full_name='tesra.AgentServer',
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    serialized_start=147,
    serialized_end=241,
    methods=[
        _descriptor.MethodDescriptor(
            name='TaskStart',
            full_name='tesra.AgentServer.TaskStart',
            index=0,
            containing_service=None,
            input_type=_PROTO,
            output_type=_PROTO,
            serialized_options=None,
        ),
        _descriptor.MethodDescriptor(
            name='TaskStop',
            full_name='tesra.AgentServer.TaskStop',
            index=1,
            containing_service=None,
            input_type=_PROTO,
            output_type=_PROTO,
            serialized_options=None,
        ),
    ])
_sym_db.RegisterServiceDescriptor(_AGENTSERVER)

DESCRIPTOR.services_by_name['AgentServer'] = _AGENTSERVER

# @@protoc_insertion_point(module_scope)
