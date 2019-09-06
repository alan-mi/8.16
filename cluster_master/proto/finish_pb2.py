# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: finish.proto

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


DESCRIPTOR = _descriptor.FileDescriptor(name='finish.proto', package='cluster', syntax='proto3', serialized_options=None, serialized_pb=_b(
    '\n\x0c\x66inish.proto\x12\x07\x63luster\"\x17\n\x03Req\x12\x10\n\x08req_args\x18\x01 \x01(\t\"\x1a\n\x03Res\x12\x13\n\x0bres_content\x18\x01 \x01(\t22\n\x08\x43omputed\x12&\n\x06\x66inish\x12\x0c.cluster.Req\x1a\x0c.cluster.Res\"\x00\x62\x06proto3'))


_REQ = _descriptor.Descriptor(
    name='Req',
    full_name='cluster.Req',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='req_args', full_name='cluster.Req.req_args', index=0,
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
    serialized_start=25,
    serialized_end=48,
)


_RES = _descriptor.Descriptor(
    name='Res',
    full_name='cluster.Res',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='res_content', full_name='cluster.Res.res_content', index=0,
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
    serialized_start=50,
    serialized_end=76,
)

DESCRIPTOR.message_types_by_name['Req'] = _REQ
DESCRIPTOR.message_types_by_name['Res'] = _RES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Req = _reflection.GeneratedProtocolMessageType('Req', (_message.Message,), dict(
    DESCRIPTOR=_REQ,
    __module__='finish_pb2'
    # @@protoc_insertion_point(class_scope:cluster.Req)
))
_sym_db.RegisterMessage(Req)

Res = _reflection.GeneratedProtocolMessageType('Res', (_message.Message,), dict(
    DESCRIPTOR=_RES,
    __module__='finish_pb2'
    # @@protoc_insertion_point(class_scope:cluster.Res)
))
_sym_db.RegisterMessage(Res)


_COMPUTED = _descriptor.ServiceDescriptor(
    name='Computed',
    full_name='cluster.Computed',
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    serialized_start=78,
    serialized_end=128,
    methods=[
        _descriptor.MethodDescriptor(
            name='finish',
            full_name='cluster.Computed.finish',
            index=0,
            containing_service=None,
            input_type=_REQ,
            output_type=_RES,
            serialized_options=None,
        ),
    ])
_sym_db.RegisterServiceDescriptor(_COMPUTED)

DESCRIPTOR.services_by_name['Computed'] = _COMPUTED

# @@protoc_insertion_point(module_scope)