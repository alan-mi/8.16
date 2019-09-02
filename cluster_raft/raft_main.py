# coding:utf-8
import asyncio
import json
import multiprocessing
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor


from cluster_demon.cluster_server import ClusterServer
from cluster_demon.utils import dc_vip


from cluster_raft import raft_init, tools, raft_grpc_pb2
import grpc

from cluster_raft import raft_grpc_pb2_grpc, raft_grpc_server
from sanic import Sanic, request, response

from cluster_raft.tools import vip_event, logger, stop_thread, spawn, up_event

from conf import CONFIG

app = Sanic(__name__)

sys.path.append("../")

@app.route('/status', methods=["GET"])
async def getStatus(request):
    res = raft_init.raft_obj.getStatus()
    return response.json(res)


@app.route('/register/<host>')
async def h_register(request, host):
    raft_init.raft_obj.addNodeToClusterDC(host)
    result = raft_init.raft_obj.getStatus()
    return response.json(result)


# 删除节点
@app.route('/unregister/<host>')
async def h_unregister(request, host):
    raft_init.raft_obj.removeNodeFromClusterDC(host)
    await asyncio.sleep(1)
    result = raft_init.raft_obj.getStatus()
    return response.json(result)


# 选举
@app.route('/election')
async def h_election(request):
    # 卸载vip重新选举
    # common.vip_restart.set()
    raft_init.raft_obj.dc_election()
    return response.json({
        'msg': 'handled election. '
    })


@app.route('/node')
async def get_all_node(request):
    # 卸载vip重新选举
    # common.vip_restart.set()
    return response.json({
        'node': raft_init.raft_obj.allNodeAddrs
    })


def vip_load():
    logger.info(vip_event.is_set())
    with grpc.insecure_channel("0.0.0.0:{}".format(CONFIG.get("raft_grpc_port"))) as chan:
        stub = raft_grpc_pb2_grpc.RaftServiceStub(channel=chan)

        # p = multiprocessing.Process(target=send_status_to_schedule, args=())
        # p.daemon = True
        cli = []
        while True:
            time.sleep(3)
            ts = int(time.time())

            try:
                res_f = stub.GetStatus.future(raft_grpc_pb2.GetStatusReq(ts=str(ts)),timeout=3)
                if res_f.result().ts == str(ts):
                    raft_status = json.loads(res_f.result().status)
                    # raft_status = raft_init.raft_obj.getStatus()
                    logger.info("vip_event {},leader {}, self_node {},isReady {}".format(vip_event.is_set(), raft_status['leader'], raft_status['self'], raft_status["isReady"]))

                    if vip_event.is_set() and raft_status['leader'] == raft_status['self'] and raft_status["state"] == 2:
                        dc_vip.vip.set_vip("up")
                        vip_event.clear()
                        logger.info("启动>>>cluster_server")
                        up_event.set()
                        cs = ClusterServer(addr="0.0.0.0:8300")
                        cs.start()
                        cli.append(cs)
                    if not vip_event.is_set() and raft_status['leader'] != raft_status['self']:
                        dc_vip.vip.set_vip("down")
                        vip_event.set()
                        logger.info("停止>>>cluster_server")
                        up_event.clear()
                        cli.pop().stop()
            except Exception as e:
                logger.info(e)
                logger.info("停止>>>cluster_server")
                for i in cli:
                    i.stop()
                continue


def start_loop(loop):
    try:
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except asyncio.CancelledError:
        loop.stop()

    except Exception as e:
        print(e)


async def raft_event_loop(raft_obj):
    alive_dict = {}
    alive_time = time.time()
    print(alive_time)
    with open("loop.log", "a") as fw:
        fw.write(alive_time)
        while True:
            try:
                await asyncio.sleep(.2)
                # 判断事件是否能执行 当启动raft——init时会进行这一步
                if tools.raft_loop.is_set():
                    now = time.time()
                    fw.write(raft_obj.isReady())
                    if raft_obj.isReady():
                        status = raft_obj.getStatus()
                        if status['state'] == 2:
                            # 配置 网卡 开启事件 vip_status
                            dc_vip.vip.set_vip('up')
                            tools.vip_event.set()
                        else:
                            # 卸载网卡
                            dc_vip.vip.set_vip('down')
                            tools.vip_event.clear()
                        an = tools.get_all_nodes_from_raft_status(status)
                        # 循环写入状态 删除不存在的状态
                        for n in an:
                            if n == status['self']:
                                alive_dict[n] = now
                            else:
                                k = 'partner_node_status_server_' + n
                                if status[k] == 2:
                                    alive_dict[n] = now
                                else:
                                    if n not in alive_dict:
                                        alive_dict[n] = now
                                    elif now - alive_dict[n] > max(
                                            2 * len(an),
                                            3000
                                    ):
                                        raft_obj.removeNodeFromCluster(n)
                                        del alive_dict[n]
                                    else:
                                        pass
                        for n in list(alive_dict.keys()):
                            if n not in an.keys():
                                del alive_dict[n]
                        print('\n{}-{} {} \n{}'.format(
                            status.get('leader'), status.get('raft_term'), len(an), an
                        ))
                        if status['leader']:
                            alive_time = time.time()
                    else:
                        alive_dict.clear()
                        dc_vip.vip.set_vip('down')
                        tools.vip_event.clear()
                    if time.time() - alive_time > 3000:
                        raft_obj.dc_election()
                        alive_time = time.time()
            except Exception as e:
                print('{}\n{}'.format(e, traceback.format_exc()))
                dc_vip.vip.set_vip('down')
                tools.vip_event.clear()


def run_server():
    p = spawn(target=vip_load, name="find_vip")
    try :
        server = grpc.server(ThreadPoolExecutor(40))
        # 将对应的任务处理函数添加到rpc server中
        raft_grpc_pb2_grpc.add_RaftServiceServicer_to_server(raft_grpc_server.RaftService(), server)
        # 这里使用的非安全接口，世界gRPC支持TLS/SSL安全连接，以及各种鉴权机制
        server.add_insecure_port("0.0.0.0:{}".format(CONFIG.get("raft_grpc_port")))
        server.start()
        # 开启服务
        #TODO 开启进程选举会报错
        app.run(
            host='0.0.0.0',
            # 8586端口 只是在muster启动
            port=CONFIG.get("raft_http_port"),
        )
    except Exception as e:
        logger.info(e)

    finally:
        stop_thread(p)
        dc_vip.vip.set_vip("down")
        exit("退出")


if __name__ == '__main__':
    run_server()




