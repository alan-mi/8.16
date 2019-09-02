import os
import time
import json
from socket import socket, AF_INET, SOCK_STREAM

import grpc
import psutil
import traceback

from cluster_demon.proto import sch_pb2_grpc, sch_pb2
from cluster_raft.tools import logger
from conf import CONFIG
from cluster_demon.utils.client_mongo import cli,Mongo


def update_shell_dc(i: dict, k: str, c: str, default: str = '') -> None:
    try:
        p = psutil.subprocess.Popen(
            c,
            stdin=psutil.subprocess.PIPE,
            stdout=psutil.subprocess.PIPE,
            shell=True
        )
        if p.stderr:
            raise OSError(p.stderr.read().decode())
        else:
            i[k] = p.stdout.read().decode()
    except Exception as e:
        logger.error('{}\n{}'.format(e, traceback.format_exc()))
        i[k] = default


def update_cpu(i: dict) -> None:
    i['cpu_count'] = psutil.cpu_count()
    i['cpu_count_physical'] = psutil.cpu_count(False)
    i['cpu_percent'] = psutil.cpu_percent()


def update_disk_usage(i: dict) -> None:
    o = psutil.disk_usage('/')
    i['disk_usage_total'] = o.total
    i['disk_usage_used'] = o.used
    i['disk_usage_free'] = o.free
    i['disk_usage_percent'] = o.percent


def update_disk_io_counters(i: dict, interval: float = 0.1) -> None:
    o = psutil.disk_io_counters()
    i['disk_io_counters_read_count'] = o.read_count
    i['disk_io_counters_write_count'] = o.write_count
    i['disk_io_counters_read_bytes'] = o.read_bytes
    i['disk_io_counters_write_bytes'] = o.write_bytes
    i['disk_io_counters_read_time'] = o.read_time
    i['disk_io_counters_write_time'] = o.write_time
    i['disk_io_counters_read_merged_count'] = o.read_merged_count
    i['disk_io_counters_write_merged_count'] = o.write_merged_count
    i['disk_io_counters_busy_time'] = o.busy_time
    time.sleep(interval)
    o_ = psutil.disk_io_counters()
    i['disk_io_counters_read_bytes_next'] = o_.read_bytes
    i['disk_io_counters_write_bytes_next'] = o_.write_bytes
    i['disk_io_counters_bytes_interval'] = interval
    i['disk_io_counters_read_bytes_rate'] = (o_.read_bytes - o.read_bytes) / interval
    i['disk_io_counters_write_bytes_rate'] = (o_.write_bytes - o.write_bytes) / interval


def update_virtual_memory(i: dict) -> None:
    o = psutil.virtual_memory()
    i['virtual_memory_total'] = o.total
    i['virtual_memory_available'] = o.available
    i['virtual_memory_percent'] = o.percent
    i['virtual_memory_used'] = o.used
    i['virtual_memory_free'] = o.free
    i['virtual_memory_active'] = o.active
    i['virtual_memory_inactive'] = o.inactive
    i['virtual_memory_buffers'] = o.buffers
    i['virtual_memory_cached'] = o.cached
    i['virtual_memory_shared'] = o.shared
    i['virtual_memory_slab'] = o.slab


def update_swap_memory(i: dict) -> None:
    o = psutil.swap_memory()
    i['swap_memory_total'] = o.total
    i['swap_memory_used'] = o.used
    i['swap_memory_free'] = o.free
    i['swap_memory_percent'] = o.percent
    i['swap_memory_sin'] = o.sin
    i['swap_memory_sout'] = o.sout


def update_net_io_counters(i: dict, interval: float = 0.1) -> None:
    o = psutil.net_io_counters()
    i['net_io_counters_bytes_sent'] = o.bytes_sent
    i['net_io_counters_bytes_recv'] = o.bytes_recv
    time.sleep(interval)
    o_ = psutil.net_io_counters()
    i['net_io_counters_bytes_sent_next'] = o_.bytes_sent
    i['net_io_counters_bytes_recv_next'] = o_.bytes_recv
    i['net_io_counters_bytes_interval'] = interval
    i['net_io_counters_bytes_sent_rate'] = (o_.bytes_sent - o.bytes_sent) / interval
    i['net_io_counters_bytes_recv_rate'] = (o_.bytes_recv - o.bytes_recv) / interval


def update_model_obj(obj: object, i: dict) -> None:
    for k, v in i.items():
        setattr(obj, k, v)


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


def get_all_nodes_from_raft_status(i: dict) -> dict:
    nodes = {}
    for k in i.keys():
        if k == 'self':
            nodes[i[k]] = 2
        if k.startswith('partner_node_status_server_'):
            nodes[k[27:]] = i[k]
    return nodes


def get_json_conf(json_path: str, sep, stop: bool = True) -> dict:
    base_conf = None
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r') as fp:
                base_conf = json.load(fp)
        else:
            raise Exception('NOT FOUND FILE!')
    except Exception as e:
        logger.warning('Parse {} Failed. \nERROR: {}'.format(json_path, e))
        if stop:
            os.sys.exit(1)
    if base_conf:
        machines_details = base_conf.pop('machines_details')
        base_conf['machines_details'] = []
        for machine in machines_details:
            machine['id'] = '{}{}{}'.format(
                base_conf.get('cluster_id'),
                sep,
                machine['id']
            )
            machine['name'] = '{}{}{}'.format(
                base_conf.get('cluster_name'),
                sep,
                machine['name']
            )
            base_conf['machines_details'].append(machine)
        return base_conf
    else:
        if stop:
            os.sys.exit(1)


def fix_localhost(port):
    return 'localhost:{}'.format(port)


def get_raft_init_nodes(i: dict) -> list:
    return ['{}:{}'.format(n, i.get('raft_port')) for n in i.get('machines')]


def get_node_gpu_count(heart_beat):
    for k, v in heart_beat.items():
        if k == "gpus":
            lastHeartbeat = time.time()
            return {k: v, "lastHeartbeat": lastHeartbeat}


def local_ip():
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(("1.1.1.1", 80))
    ip = s.getsockname()[0]
    return ip


def heart_beat():
    mongo = Mongo(host='192.168.137.2', port=27017, db="cluster", table="machines")
    heart_beat_body = {}
    LOCAL_HOST = local_ip()
    grpc_public_port = CONFIG.get("grpc_public_port")
    heart_beat_body["callbackAddress"] = "{sch_ip}:{port}".format(
        sch_ip=CONFIG["sch_callback_ip"],
        port=CONFIG["grpc_public_port"] if grpc_public_port else int(
            CONFIG["sch_callback_port_prefix"]) + int(LOCAL_HOST.split(".")[-1]),
    )
    heart_beat_body["clusterID"] = CONFIG.get("cluster_id")
    heart_beat_body["gpus"] =[{"model":k,"count":v} for k,v in mongo.use_gpu_by_num().items()]
    return heart_beat_body


def login_schedule():
    flag = False
    while not flag:
        body = heart_beat()
        time.sleep(3)
        with grpc.insecure_channel(":".join(CONFIG["sch_grpc_server"])) as channel:
            try:
                stub = sch_pb2_grpc.SkylarkStub(channel=channel)
                res = stub.Login(sch_pb2.Proto(version=1, seq=1, timestamp=int(time.time()),
                                               body=json.dumps(body).encode()), timeout=10)
                logger.warning("注册集群成功: SCHEDULE=>{}  STATUS<={}".format(body, res.body.decode()))
                flag = True
                break
            except Exception as e:
                logger.warning("注册集群失败: SCHEDULE=>{}  ERROR<={}".format(body, e))



def heart_schedule():
    while True:
        body = heart_beat()
        time.sleep(3)
        with grpc.insecure_channel(":".join(CONFIG["sch_grpc_server"])) as channel:
            try:
                stub = sch_pb2_grpc.SkylarkStub(channel=channel)
                res = stub.HeartBeat(
                    sch_pb2.Proto(version=1, seq=1, timestamp=int(time.time()),body=json.dumps(body).encode()),
                    timeout=10)
                logger.warning("心跳任务发送: SCHEDULE=>{}  STATUS<={}".format(body, res.body.decode()))
            except Exception as e:
                logger.warning("心跳任务失败: SCHEDULE=>{}  ERROR<={}".format(body, e))

def send_status_to_schedule():
    logger.info("心跳任务启动")
    login_schedule()
    heart_schedule()

def kill_children():
    import psutil
    ps = psutil.Process()
    print(ps.pid, '当前进程', os.getpid(), os.getppid())
    print(ps.children(recursive=True), "child")
    if ps.children(recursive=True):
        for i in ps.children(recursive=True):
            print(i.pid, "child pid")
            #
            print(i.status())
            i.terminate()
            print(i.status())
            # i.send_signal(sig=9)
    print(ps.status())

if __name__ == '__main__':
    import multiprocessing
    p = multiprocessing.Process(target=send_status_to_schedule,args=())
    p.daemon=True
    p.start()
    print(p.pid,"子进程")
    import psutil
    ps = psutil.Process()
    print(ps.pid,'当前进程',os.getpid(),os.getppid())
    print(ps.children(recursive=True),"child")
    for i in ps.children(recursive=True):
        print(i.pid,"child pid")
        #
        print(i.status())
        # i.kill()
        print(i.status())
        # i.send_signal(sig=9)

    print(p.is_alive(), "子进程是否活着")
    print(ps.status())
    time.sleep(10)
