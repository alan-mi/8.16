"""
This file is for helping function.
"""

import json
import grpc
import time
import socket
import random
import base64
import requests
import retrying
import traceback
from functools import wraps
from requests.utils import urlparse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from multiprocessing import (
    Event,
    Queue
)


from cluster_raft import (
    raft_grpc_pb2,
    raft_grpc_pb2_grpc
)
from cluster_master.utils import (
    dc_vip,
    tools
)


SERVER_TYPE = 'slave'

vip_status = Event()
vip_restart = Event()

master_status = Event()
master_restart = Event()

slave_status = Event()
slave_restart = Event()

raft_loop = Event()

vip = dc_vip.vip
current_ip = vip.ip
CLUSTER_CONF = cluster_config.CLUSTER_CONF
PROJECT_HOME = cluster_config.PROJECT_HOME
CONFIG_HOME = cluster_config.CONFIG_HOME

local_grpc_stub = raft_grpc_pb2_grpc.RaftServiceStub(grpc.insecure_channel(
    '{}:{}'.format(vip.ip, CLUSTER_CONF.get('raft_grpc_port'))
))


def get_raft_init_nodes(i: dict) -> list:
    return ['{}:{}'.format(n, i.get('raft_port')) for n in i.get('machines')]


def get_id_by_ip(i: str) -> str:
    return list(
        filter(
            lambda x: x['ip'] == i,
            CLUSTER_CONF.get('machines_details')))[0]['id']


def get_id_by_ip_port(i: str) -> str:
    i = i.split(':')[0]
    return get_id_by_ip(i)


def get_details_by_id(i: str) -> dict:
    return list(
        filter(
            lambda x: x['id'] == i,
            CLUSTER_CONF.get('machines_details')))[0]


def get_details_by_ip(i: str) -> dict:
    return list(
        filter(
            lambda x: x['ip'] == i,
            CLUSTER_CONF.get('machines_details')))[0]


def get_details_by_ip_port(i: str) -> dict:
    return list(
        filter(
            lambda x: x['ip'] == i.split(':')[0],
            CLUSTER_CONF.get('machines_details')))[0]


raft_port = CLUSTER_CONF.get('raft_port')
raft_cluster_machines = CLUSTER_CONF.get('raft_cluster_machines')
current_node = '{}:{}'.format(current_ip, raft_port)
other_nodes = ['{}:{}'.format(ip, raft_port)
               for ip in raft_cluster_machines if ip != current_ip]

current_node_info = get_details_by_ip(current_ip)

ai_server = '{}:{}'.format(current_ip, CLUSTER_CONF.get('ai_server_port'))


def cluster_auth(func):
    @wraps(func)
    def handle_request(request, *args, **kwargs):
        try:
            port = CLUSTER_CONF.get('{}_port'.format(SERVER_TYPE), '')
            if '{}:{}'.format(
                    request.environ.get(
                        'REMOTE_ADDR',
                        ''),
                    port) == base64.b64decode(
                    request.POST.get(
                    'authKey',
                    '').encode()).decode() and request.environ.get(
                        'HTTP_AGENT',
                    '').lower() == CLUSTER_CONF.get('agent'):
                return func(request, *args, **kwargs)
            else:
                res = JsonResponse({'result': 421, 'msg': 'auth failed!'})
                res.status_code = 421
                return res
        except Exception as e:
            res = JsonResponse(
                {'result': 500, 'msg': '{}\n{}'.format(e, traceback.format_exc())})
            res.status_code = 500
            return res
    return handle_request


def get_request_info(host=current_ip):
    req = {
        'req_master': {
            'authKey': '',
            'authBase': "{}:{}".format(host, CLUSTER_CONF.get('master_port')),
            'agent': CLUSTER_CONF.get('agent'),
        },
        'req_slave': {
            'authKey': '',
            'authBase': "{}:{}".format(host, CLUSTER_CONF.get('slave_port')),
            'agent': CLUSTER_CONF.get('agent'),
        },
    }
    for k, v in req.items():
        req[k]['authKey'] = base64.b64encode(v['authBase'].encode()).decode()
    return req


REQ_BASE = get_request_info(current_ip)


@retrying.retry(
    stop_max_attempt_number=10,
    wait_random_min=100,
    wait_random_max=1000
)
def get_raft_status(ts: float) -> dict:
    ts = str(ts)
    res_f = local_grpc_stub.GetStatus.future(
        raft_grpc_pb2.GetStatusReq(ts=ts), timeout=1)
    if res_f.result().ts == ts:
        return json.loads(res_f.result().status)
    else:
        raise Exception('request and response is not matched. ')
    # ts = str(ts)
    # res = local_grpc_stub.GetStatus(raft_grpc_pb2.GetStatusReq(ts=ts), timeout=1)
    # if res.ts == ts:
    #     return json.loads(res.status)
    # else:
    #     raise Exception('request and response is not matched. ')


def get_is_registered(
        ts: float,
        need_set: bool = False,
        set_status: bool = True) -> dict:
    ts = str(ts)
    if need_set:
        res_f = local_grpc_stub.IsRegistered.future(
            raft_grpc_pb2.IsRegisteredReq(
                ts=ts, need_set=need_set, set_status=set_status))
    else:
        res_f = local_grpc_stub.IsRegistered.future(
            raft_grpc_pb2.IsRegisteredReq(ts=ts))
    if res_f.result().ts == ts:
        return res_f.result().status
    else:
        raise Exception('request and response is not matched. ')
    # ts = str(ts)
    # if need_set:
    #     res = local_grpc_stub.IsRegistered(raft_grpc_pb2.IsRegisteredReq(
    #         ts=ts,
    #         need_set=need_set,
    #         set_status=set_status
    #     ))
    # else:
    #     res = local_grpc_stub.IsRegistered(raft_grpc_pb2.IsRegisteredReq(
    #         ts=ts
    #     ))
    # if res.ts == ts:
    #     return res.status
    # else:
    #     raise Exception('request and response is not matched. ')


@retrying.retry(
    stop_max_attempt_number=3,
    # wait_random_min=10,
    # wait_random_max=100
)
def post_then_get_json(**kwargs):
    return requests.post(**kwargs).json()


@retrying.retry(
    stop_max_attempt_number=10,
    # wait_random_min=10,
    # wait_random_max=100
)
def check_online(url):
    _url = urlparse(url)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    s.connect((_url.hostname, _url.port))
    s.shutdown(2)


def params_check(method, check_dict):
    def handle_func(func):
        def handle_args(request, *args, **kwargs):
            check_it = check_dict.get(func.__name__, {}).get(method, [])
            method_params = getattr(request, method)
            params_dict = {}
            if all(map(lambda x: x is not None, [
                   method_params.get(k, None) for k in check_it])):
                params_dict.update({k: method_params.get(k) for k in check_it})
                return func(request, params_dict, *args, **kwargs)
            else:
                return JsonResponse({
                    'message': '(method){} them in {} for this operation. '.format(method, check_it),
                    'status_code': 402
                }, status=402)
        return handle_args
    return handle_func


@csrf_exempt
def test_api(request, *args, **kwargs):
    ts = time.time()
    req_base = get_request_info(request.environ.get('REMOTE_ADDR'))
    req_base['host_ip'] = vip.ip
    req_base['raft_status'] = get_raft_status(ts=ts)
    return JsonResponse({'result': 0, 'msg': req_base})


@csrf_exempt
def status(request, *args, **kwargs):
    res = JsonResponse({'result': 0, 'msg': 'online'})
    res.status_code = random.choice([200] * 20 + [201])
    return res


def undefined_operation(request, *args, **kwargs):
    res = JsonResponse({'result': 222, 'msg': 'undefined operation'})
    res.status_code = 222
    return res


def get_cn_an(raft_status=None):
    resp = None
    cn = '{}:{}'.format(vip.ip, CLUSTER_CONF.get('raft_port'))
    if not raft_status:
        try:
            while True:
                vip.set_vip('down', v=False)
                resp1 = requests.get('http://{}:{}/register/{}'.format(
                    vip.vip,
                    CLUSTER_CONF.get('raft_http_port'),
                    cn
                )).json()
                an = list(tools.get_all_nodes_from_raft_status(resp1).keys())
                if cn in an:
                    break
        except Exception as e:
            # tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
            tools.logger.info(
                'tried to get status from {} failed, trying other ways.'.format(
                    vip.vip))
            init_nodes = tools.get_raft_init_nodes(CLUSTER_CONF)
        else:
            init_nodes = an
    elif raft_status['leader']:
        an = list(tools.get_all_nodes_from_raft_status(raft_status).keys())
        return cn, an
    else:
        init_nodes = list(
            tools.get_all_nodes_from_raft_status(raft_status).keys())
    try:
        for i in init_nodes:
            if i == cn:
                continue
            try:
                while True:
                    resp = requests.get('http://{}:{}/register/{}'.format(
                        i.split(':')[0],
                        CLUSTER_CONF.get('raft_http_port'),
                        cn
                    )).json()
                    an = list(
                        tools.get_all_nodes_from_raft_status(resp).keys())
                    if cn in an:
                        break
            except Exception as e:
                # tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                tools.logger.info(
                    'tried to get status from {} failed, trying other ways.'.format(i))
            else:
                break
        if not resp:
            raise Exception('init nodes...')
    except Exception as e:
        # tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
        tools.logger.info(
            'tried to get status from online status failed, trying init nodes: {}.'.format(init_nodes))
        an = init_nodes
    else:
        an = list(tools.get_all_nodes_from_raft_status(resp).keys())
    return cn, an
