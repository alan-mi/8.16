# coding:utf-8

import copy
import time

from pysyncobj import SyncObj, SyncObjConf, replicated


class DCSyncObj(SyncObj):
    def __init__(self, selfNodeAddr, allNodeAddrs):
        if selfNodeAddr not in allNodeAddrs:
            allNodeAddrs.append(selfNodeAddr)
        allNodeAddrs = list(set(allNodeAddrs))
        self.selfNodeAddr = copy.deepcopy(selfNodeAddr)
        self.allNodeAddrs = copy.deepcopy(allNodeAddrs)
        self.__task_status = {}
        if selfNodeAddr in allNodeAddrs:
            allNodeAddrs.remove(selfNodeAddr)
        super(DCSyncObj, self).__init__(
            selfNodeAddr,
            allNodeAddrs,
            SyncObjConf(dynamicMembershipChange=True)
        )

    def addNodeToClusterDC(self, value):
        self.addNodeToCluster(value)
        self.add_node(value)

    def removeNodeFromClusterDC(self, value):
        self.removeNodeFromCluster(value)
        self.remove_node(value)

    @replicated
    def add_node(self, value):
        print("添加节点",value)
        print("添加节点",self.allNodeAddrs)
        if value not in self.allNodeAddrs:
            self.allNodeAddrs.append(value)

    @replicated
    def remove_node(self, value):
        print("删除节点", value)
        print("删除节点", self.allNodeAddrs)
        if value in self.allNodeAddrs:
            self.allNodeAddrs.remove(value)

    def dc_election(self):
        # 检测完全关闭
        while not getattr(getattr(getattr(
                self, '_SyncObj__server'
        ), '_TcpServer__socket'), '_closed'):
            self.destroy()
        else:
            status = self.getStatus()
            self.__init__(self.selfNodeAddr, self.allNodeAddrs)
        # 检测是否打开
        while getattr(getattr(getattr(
                self, '_SyncObj__server'
        ), '_TcpServer__socket'), '_closed'):
            # while not self.isReady():
            pass

        else:
            print('{} is in raft cluster. \n{}'.format(self.selfNodeAddr, self.allNodeAddrs))

    @replicated
    def set_task_status(self,task):
        self.__task_status = task

    def get_task_status(self):
        return self.__task_status


