import re
import time
import grpc
import random
import asyncio
import datetime
import traceback
from functools import reduce

from protocol import (
    cluster_strategy_pb2,
    cluster_strategy_pb2_grpc
)
from cluster_monitor.utils import (
    common,
    tools,
    dc_orm,
    dc_mongo
)


sqlite_obj = dc_orm.SqliteDB()


async def raft_damon(raft_obj):
    called_weights = False
    is_send = False
    round_count = 0
    pre_master, cur_master = common.current_node, common.current_node
    try:
        while True:
            not_online = []
            now = datetime.datetime.now()
            if raft_obj.isReady():
                a = time.time()
                status = raft_obj.getStatus()
                b = time.time()
                tools.logger.debug('{}'.format(is_send))
                if cur_master != status['leader'] and status['leader']:
                    pre_master, cur_master = cur_master, status['leader']
                if common.current_node == status.get('leader'):
                    raft_obj.term_info_update()
                    common.vip_status.set()
                    common.vip.set_vip('up')
                    is_online = common.vip.check_vip()
                    if is_online:
                        if not is_send:
                            try:
                                with grpc.insecure_channel(common.CLUSTER_CONF.get('cluster_lv1_call_center')) as \
                                        channel:
                                    stub = cluster_strategy_pb2_grpc.StrategyServiceStub(channel)
                                    resp = stub.ClusterMasterChangeNotify(
                                        cluster_strategy_pb2.ClusterMasterChangeNotifyRequest(
                                            cluster_name=common.CLUSTER_CONF['cluster_name'],
                                            pre_master_name='{}-{}'.format(
                                                pre_master,
                                                tools.get_id_by_host_port(pre_master),
                                            ),
                                            cur_master_name='{}-{}'.format(
                                                cur_master,
                                                tools.get_id_by_host_port(cur_master),
                                            ),
                                            # pre_master_name=raft_obj.last_n_term_info(2).get('leader'),
                                            # cur_master_name=status.get('leader'),
                                            timestamp=int(now.timestamp()),
                                        ),
                                        timeout=1
                                    )
                                    tools.logger.warning('{}'.format(resp.status) * 100)
                                    is_send = True
                            except Exception as e:
                                tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                    else:
                        is_send = False
                    if not raft_obj.dc_get_registered():
                        raft_obj.dc_set_registered(True)
                        try:
                            gpu_dict = dc_mongo.db.get_collection('gpu').find_one()
                        except Exception as e:
                            tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                        ips = [
                            ip for ip in common.CLUSTER_CONF.get('raft_cluster_machines')
                            if ip == common.vip.ip or status.get('partner_node_status_server_{}:{}'.format(
                                ip, common.CLUSTER_CONF.get('raft_port')
                            )) == 2
                        ]
                        try:
                            with grpc.insecure_channel(common.CLUSTER_CONF.get('cluster_lv1_call_center')) as channel:
                                stub = cluster_strategy_pb2_grpc.StrategyServiceStub(channel)
                                address = '{}:{}'.format(
                                            common.CLUSTER_CONF.get('public_ip'),
                                            common.CLUSTER_CONF.get('grpc_port_public'),
                                        )
                                downlink_bandwidth = float(re.match(
                                    r'(?P<m>\d+)M',
                                    common.CLUSTER_CONF.get('network_info')['DownlinkBandwidth']
                                ).groupdict()['m']) * 1024 * 1024
                                telecom_operators = common.CLUSTER_CONF.get('network_info')['ISP_lite']
                                longitude = common.CLUSTER_CONF.get('location')['1'].get('lng')
                                latitude = common.CLUSTER_CONF.get('location')['1'].get('lat')
                                count_1070Ti = reduce(
                                    lambda x, y: x + y, list(map(
                                        lambda ip: tools.get_details_by_ip(
                                            ip.split(':')[0],
                                            common.CLUSTER_CONF
                                        )['gpu']['GeForce GTX 1070 Ti'], ips
                                    ))
                                )
                                count_1080Ti = reduce(
                                    lambda x, y: x + y, list(map(
                                        lambda ip: tools.get_details_by_ip(
                                            ip.split(':')[0],
                                            common.CLUSTER_CONF
                                        )['gpu']['GeForce GTX 1080 Ti'], ips
                                    ))
                                )
                                # count_1070Ti=gpu_dict['max_gpu_a']
                                # count_1080Ti=gpu_dict['max_gpu_b']
                                timestamp = int(time.time())
                                master_name = '{}-{}'.format(
                                    status.get('leader'),
                                    tools.get_id_by_host_port(status.get('leader')),
                                )
                                cluster_name = common.CLUSTER_CONF['cluster_name']
                                cluster_id = common.CLUSTER_CONF['cluster_id']
                                cluster_public_url = 'http://{}:{}/master/api'.format(
                                    common.CLUSTER_CONF['public_ip'],
                                    common.CLUSTER_CONF['public_port'],
                                )
                                if common.current_node == raft_obj.getStatus()['leader']:
                                    resp = stub.ClusterRegister(cluster_strategy_pb2.ClusterRegisterRequest(
                                        address=address,
                                        downlink_bandwidth=downlink_bandwidth,
                                        telecom_operators=telecom_operators,
                                        longitude=longitude,
                                        latitude=latitude,
                                        count_1070Ti=count_1070Ti,
                                        count_1080Ti=count_1080Ti,
                                        # count_1070Ti=count_1070Ti,
                                        # count_1080Ti=count_1080Ti,
                                        timestamp=timestamp,
                                        master_name=master_name,
                                        cluster_name=cluster_name,
                                        cluster_id=cluster_id,
                                        cluster_public_url=cluster_public_url,
                                    ),
                                        timeout=1
                                    )
                                else:
                                    resp = stub.ClusterRegister(cluster_strategy_pb2.ClusterRegisterRequest(
                                        address=address,
                                        downlink_bandwidth=downlink_bandwidth,
                                        telecom_operators=telecom_operators,
                                        longitude=longitude,
                                        latitude=latitude,
                                        count_1070Ti=count_1070Ti,
                                        count_1080Ti=count_1080Ti,
                                        # count_1070Ti=count_1070Ti,
                                        # count_1080Ti=count_1080Ti,
                                        timestamp=timestamp,
                                        master_name=master_name,
                                        cluster_name=cluster_name,
                                        cluster_id=cluster_id,
                                        cluster_public_url=cluster_public_url,
                                    ),
                                        timeout=1
                                    )
                                    tools.logger.warning('{}'.format(resp.status*3) * 100)
                                tools.logger.warning('{}'.format(resp.status*2) * 100)
                        except Exception as e:
                            tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                            raft_obj.dc_set_registered(False)
                    raft_obj.is_alive_then_clean(clean=False)
                    try:
                        for on in raft_obj.allNodeAddrs:
                            if on == status.get('leader'):
                                await dc_mongo.a_db['machine'].update_one(
                                    {'address': on.split(':')[0]},
                                    {'$set': {'role': 'master', 'is_alive': 2, 'dc_update_time': now}},
                                    upsert=True
                                )
                            elif status.get('partner_node_status_server_{}'.format(on), None) in [1, 2]:
                                await dc_mongo.a_db['machine'].update_one(
                                    {'address': on.split(':')[0]},
                                    {'$set': {
                                        'role': 'worker',
                                        'is_alive': status.get('partner_node_status_server_{}'.format(on), None),
                                        'dc_update_time': now,
                                    }},
                                    upsert=True
                                )
                            else:
                                await dc_mongo.a_db['machine'].update_one(
                                    {'address': on.split(':')[0]},
                                    {'$set': {
                                        'role': 'worker',
                                        'is_alive': status.get('partner_node_status_server_{}'.format(on), 0),
                                        'dc_update_time': now,
                                    }},
                                )
                                not_online.append({
                                    on: status.get('partner_node_status_server_{}'.format(on), None)
                                })
                    except Exception as e:
                        tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                    common.raft_node_disable.clear()
                    common.raft_node_enable.set()
                else:
                    is_send = False
                    common.vip_status.clear()
                    common.vip.set_vip('down', v=False)
                c = time.time()
                if called_weights:
                    pass
                else:
                    if common.current_node == status.get('leader') \
                            and random.random() > raft_obj.weights[common.current_node]:
                        raft_obj.init()
                    else:
                        pass
                    called_weights = True
                d = time.time()
                if common.vip_restart.is_set():
                    raft_obj.init()
                    called_weights = False
                    common.vip_restart.clear()
                e = time.time()
                f = time.time()
                h = time.time()
                if not round_count % 100:
                    tools.logger.info('Term-{:<5} Master: {}, Not_Online: {} \na-b: {:.3f} b-c: {:.3f} c-d: '
                                        '{:.3f} d-e: {:.3f} e-f: {:.3f} f-h: {:.3f} round_count: {}'.format(
                                            status.get('raft_term'),
                                            status.get('leader'),
                                            not_online,
                                            b-a, c-b, d-c, e-d, f-e, h-f, round_count))
                round_count += 1
            try:
                op, info = common.raft_slave_queue.get_nowait()
            except Exception as e:
                tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                op, info = None, None
            if op:
                if op == 'add':
                    raft_obj.allNodeAddrs = tools.get_all_nodes_from_raft_status(info)
                    raft_obj.init()
                if op == 'remove':
                    try:
                        raft_obj.destory()
                    except Exception as e:
                        tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
            if common.raft_node_disable.is_set() and raft_obj.check_self_status():
                try:
                    raft_obj.destory()
                except Exception as e:
                    tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
                common.raft_node_disable.clear()
                common.raft_node_enable.wait()
                raft_obj.init_base_online_nodes()
                common.raft_node_disable.clear()
                common.raft_node_enable.set()
    except asyncio.CancelledError:
        tools.logger.warning('Cancelled Raft_Daemon Executor. ')
        raise
    except KeyboardInterrupt:
        tools.logger.warning('KeyboardInterrupt. ')
        raise
    except Exception as e:
        tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))


def start_loop(loop):
    try:
        loop.run_forever()
    except asyncio.CancelledError:
        tools.logger.warning('Stopped Start Loop. ')
        raise
    except KeyboardInterrupt:
        tools.logger.warning('KeyboardInterrupt Were Detected. ')
        raise
