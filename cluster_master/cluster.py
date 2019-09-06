# coding:utf-8
import sys
import time

from cluster_master.cluster_server import ClusterServer
from cluster_master.utils.tools import login_and_update
from cluster_raft.tools import logger, up_cluster_event, stop_thread
from cluster_raft.raft_main import run_server, spawn
from multiprocessing import Process


class Cluster:
    def __init__(self):
        pass

    def start_heart_cluster(self):
        # 循环检测需要一个标识判断
        flag = True
        a = []
        b = []
        while True:
            time.sleep(2)
            if up_cluster_event.is_set() and flag:
                logger.info("启动程序>>>HeartSchedule>>>ClusterServer")
                p = spawn(target=login_and_update, name="heartbeat")
                cs = ClusterServer(addr="0.0.0.0:8300")
                cs.start()
                a.append(p)
                b.append(cs)
                flag = False
            elif not up_cluster_event.is_set():
                flag = True
                if all([a, b]):
                    logger.info("关闭程序>>>HeartSchedule>>>ClusterServer")
                    b.pop().stop()
                    stop_thread(a.pop())

    def up_cluster_server(self):
        p = spawn(target=self.start_heart_cluster)
        return p

    def raft_server(self):
        logger.info("启动raft程序...")
        run_server()

    def test(self):
        while True:
            time.sleep(1)
            logger.info("test")

    def run(self):
        """
        启动raft server
        根据事件机制触发leader程序

        :return:
        """

        self.up_cluster_server()
        self.raft_server()


if __name__ == '__main__':
    cs = Cluster()
    cs.run()
