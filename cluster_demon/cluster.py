# coding:utf-8
import sys
import time


from cluster_demon.utils.tools import send_status_to_schedule, kill_children
from cluster_raft.tools import up_event, stop_thread, logger
from cluster_raft.raft_main import run_server, spawn


class Cluster_Server:
    def __init__(self):
        pass

    def test(self):
        flag = True
        a = []
        while True:
            time.sleep(2)
            if up_event.is_set() and flag:
                logger.info("启动心跳程序>>>Schedule")
                p = spawn(target=send_status_to_schedule)
                a.append(p)
                flag = False
            elif not up_event.is_set():
                flag = True
                if a:
                    stop_thread(a.pop())

    def heart_beat(self):

        p = spawn(target=self.test)
        return p

    def raft_server(self):
        logger.info("启动raft程序...")
        run_server()

    def run(self):
        self.heart_beat()
        self.raft_server()


if __name__ == '__main__':
    cs = Cluster_Server()
    cs.run()
