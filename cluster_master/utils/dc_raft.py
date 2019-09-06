#!/usr/bin/env python
"""
This file is startup.
"""

import ctypes
import time
import raftos
import random
import inspect
import asyncio
import datetime
from multiprocessing.dummy import Process as Thread

from cluster_monitor.utils import common


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class RaftDaemon(object):
    def __init__(self):
        raftos.configure({
            'log_path': '/tmp',
            'serializer': raftos.serializers.JSONSerializer
        })
        self.conf = common.CLUSTER_CONF
        self.clusters = [
            '{}:{}'.format(cluster, self.conf.get('raft_port')) for
            cluster in self.conf.get('raft_cluster_machines') if
            cluster != common.vip.ip
        ]
        self.node = '{}:{}'.format(common.vip.ip, self.conf.get('raft_port'))
        self.raft_thread = None
        self.monitor_thread = None

    def start_raft(self):
        common.raft_status.clear()
        common.vip_status.clear()
        common.raft_restart.clear()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(raftos.register(self.node, cluster=self.clusters))
        loop.run_until_complete(self.run_node())

    def start(self):
        self.raft_thread = Thread(target=self.start_raft, args=())
        self.raft_thread.daemon = True
        self.raft_thread.start()
        self.monitor_thread = Thread(target=self.run_monitor, args=())
        # self.monitor_thread.daemon = True
        self.monitor_thread.start()
        pass

    def run_monitor(self):
        # while True:
        #     if not self.thread.is_alive() or common.raft_restart.wait(0):
        #         tools.logger.info('raft daemon restarting... ')
        #         self.restart()
        while True:
            print(self.raft_thread.getName(), self.raft_thread.is_alive())
            time.sleep(5)
            stop_thread(self.raft_thread)
            self.raft_thread = Thread(target=self.start_raft, args=())
            self.raft_thread.daemon = True
            self.raft_thread.start()

    async def run_node(self):
        data_id = raftos.Replicated(name='data_id')
        data = raftos.ReplicatedDict(name='data')
        data_list = raftos.ReplicatedList(name='data_list')
        while True:
            await raftos.wait_until_leader(self.node)
            await asyncio.sleep(2)
            current_id = random.randint(1, 1000)
            data_map = {
                str(current_id): {
                    'created_at': datetime.datetime.now().strftime('%d/%m/%y %H:%M')}}
            await data_id.set(current_id)
            await data.update(data_map)
            await data_list.append(data_map)


if __name__ == '__main__':
    RaftDaemon().start()
