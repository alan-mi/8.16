# coding:utf-8
import select
import sys
import threading
import time

from cluster_master.cluster_server import ClusterServer
from cluster_master.utils.tools import login_and_update, PollableQueue
from cluster_raft.tools import logger, up_cluster_event, stop_thread
from cluster_raft.raft_main import run_server, spawn
from multiprocessing import Process

from conf import CONFIG

q1 = PollableQueue()


class Cluster:
    def __init__(self):
        pass

    def consumer(self, que):
        a = []
        b = []
        while True:
            can_read, _, _ = select.select(que, [], [])
            for r in can_read:
                print(threading.current_thread().getName(), "============")
                item = r.get()
                print(item)
                if item == "start":
                    print("启动服务")
                    logger.info("启动程序   HeartSchedule >>> {}    ClusterServer >>>{}".format(
                        ":".join(CONFIG["sch_grpc_server"]), CONFIG.get("master_port")))
                    p = spawn(target=login_and_update, name="heartbeat")

                    cs = ClusterServer(
                        addr="0.0.0.0:{}".format(
                            CONFIG.get("master_port")))
                    cs.start()
                    a.append(p)
                    b.append(cs)
                else:
                    print("关闭服务")
                    logger.info("关闭程序>>>HeartSchedule>>>ClusterServer")

                    if b or a:
                        b.pop().stop()
                        stop_thread(a.pop())

    def start_heart_cluster(self):
        # 循环检测需要一个标识判断
        flag = True
        a = []
        b = []
        while True:
            time.sleep(.5)
            if up_cluster_event.is_set() and flag:
                logger.info("启动程序   HeartSchedule >>> {}    ClusterServer >>>{}".format(
                    ":".join(CONFIG["sch_grpc_server"]), CONFIG.get("master_port")))
                p = spawn(target=login_and_update, name="heartbeat")
                cs = ClusterServer(
                    addr="0.0.0.0:{}".format(
                        CONFIG.get("master_port")))
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

    def start_heart_cluster_test(self):
        spawn(target=self.consumer, args=([q1],))

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
        # p = Process(target=self.test)
        # p.daemon = True
        # p.start()
        # self.up_cluster_server()
        self.start_heart_cluster_test()
        self.raft_server()


if __name__ == '__main__':
    cs = Cluster()
    cs.run()
