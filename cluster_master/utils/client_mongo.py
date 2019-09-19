# coding:utf-8
import copy
import time
from datetime import datetime
from functools import wraps

import pymongo
import collections

from cluster_master.utils.tools import min_time_lead
from cluster_raft.tools import logger
from conf import CONFIG

MONGOHEARTIME = 5


def connect(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        count = 1
        while True:
            try:
                self.client.admin.command("ping")
                logger.info("连接mongo")
            except Exception as e:
                logger.info("第{}连接数据库失败...{}".format(count, e))
                count = count + 1
            else:
                break
            if count == 4:
                exit("退出")

        return func(self, *args, **kwargs)

    return wrapper


class Mongo:
    def __init__(self, host, db="cluster", table="machines"):
        self.db = db
        self.table = table
        self.client = pymongo.MongoClient(host=host,
                                          readPreference="primaryPreferred",
                                          replicaSet="testrepl",
                                          connectTimeoutMS=100,
                                          serverSelectionTimeoutMS=100)
        # self.connect()
        self.db = self.client[db]
        self.table = self.db[table]

    def add_data(self, data):
        self.table.insert_one(data)

    def find_data(self, rule):
        return self.table.find(rule)

    def chooice_machine_by_heart(self):
        """
        获取活着的机器
        :return: 集群信息
        """
        rule = {'ctrlAvailable': 'Y'}
        rule.update({"heartBeat": {"$gte": min_time_lead(MONGOHEARTIME)}})
        print(rule)
        machines = self.find_data(rule)
        return machines

    def free_gpu_by_task_id(self, task_id):
        """
        释放gpu
        :param task_id: 任务id
        :return: None
        """
        rule = {"gpus.status": task_id}
        for task in cli.find_data(rule):
            for gpu in task["gpus"]:
                if gpu["status"] == task_id:
                    gpu["status"] = None
            print(task)
            cli.table.update(rule, task)

    def use_gpu_by_num(self):
        '''
        获取所有的可用gpu
        :return: all_gpu
        '''
        res = self.table.aggregate(
            [{"$match": {"heartBeat": {"$gte": min_time_lead(MONGOHEARTIME)}, "gpus.status": None}},
             {"$project": {"gpus": 1, "_id": 0}},
             {"$unwind": "$gpus"}])
        it = [gpu["gpus"]["model"] for gpu in res if not gpu["gpus"]["status"]]
        all_gpu = collections.Counter(it)
        return all_gpu

    def chooice_use_gpu_by_num(self, need_gpus, task_id):
        task = {}
        mac = {}
        for model in need_gpus:
            rule = {
                "heartBeat": {
                    "$gte": min_time_lead(MONGOHEARTIME)},
                "gpus.status": None,
                "gpus.model": model["model"]}
            res = self.table.find(rule).sort('heartBeat', pymongo.DESCENDING)
            logger.info(model["count"])
            for machine in res:
                for gpu in machine["gpus"]:
                    if gpu.get("model") == model["model"] and not gpu.get(
                            "status") and model["count"] > 0:
                        model["count"] -= 1
                        gpu["status"] = task_id
                        if not mac.get(machine["machineID"]):
                            mac[machine["machineID"]] = [gpu["id"]]
                        else:
                            mac[machine["machineID"]].append(gpu["id"])
                self.table.update({"_id": machine["_id"]}, machine)
                if model["count"] == 0:
                    break
        task["taskID"] = task_id
        task["machines"] = mac
        logger.info(task)
        return task

    def compare_gpu(self, gpus):
        """
        判断gpu是否够用
        :param gpus: [{"model": "GeForce GTX 1080 Ti", "count": 2}, {"model": "GeForce GTX 1070 Ti", "count": 1}]
        :return: bool
        """
        need_gpu = {i["model"]: i["count"] for i in gpus}
        all_gpu_counter = self.use_gpu_by_num()
        for model, count in need_gpu.items():
            if all_gpu_counter[model] < count:
                return False
        return True

    def insert_update(self, machine):
        """
        心跳逻辑 查找当前心跳机器，不存在则插入，心跳超时重新插入，如果有任务只更新时间忽略超时
        :param machine:
        :return:
        """
        doc = self.table.find_one({"machineID": machine["machineID"]})
        machine.update({"heartBeat": min_time_lead()})
        if not doc:
            self.add_data(machine)
        else:
            if doc.get("heartBeat") < min_time_lead(MONGOHEARTIME):
                for gpu in doc.get("gpus"):
                    if gpu["status"]:
                        self.table.update_one(
                            doc, {
                                "$set": {
                                    "heartBeat": min_time_lead()}})
                        break
                else:
                    self.table.delete_one(doc)
                    self.table.insert_one(machine)
                    self.table.update_one(
                        machine, {
                            "$set": {
                                "heartBeat": min_time_lead()}})
            else:
                self.table.update_one(
                    doc, {
                        "$set": {
                            "heartBeat": min_time_lead()}})


a = {
    "machineID": "_003|_039",
    "clusterID": "_003",
    "ctrlAvailable": "N",
    "gpus": [
        {
            "model": "GeForce GTX 1070 Ti",
            "id": 2,
            "status": None
        },
        {
            "model": "GeForce GTX 1080 Ti",
            "id": 0,
            "status": None
        },
        {
            "model": "GeForce GTX 1080 Ti",
            "id": 3,
            "status": None
        }
    ],
}
mongo_host = CONFIG.get("mongo_center")
cli = Mongo(host=mongo_host)

# cli.add_data(a)
task_id = None

GPU_1 = "GeForce GTX 1070 Ti"
GPU_2 = "GeForce GTX 1080 Ti"


def use_gpu_by_model():
    rule = {'ctrlAvailable': 'N', "gpus.status": "adf"}
    print(list(cli.find_data(rule)))
    cli.table.update_one({""}, rule)


if __name__ == '__main__':
    # free_gpu_by_task_id("TSK01")
    # use_gpu_by_model()
    # cli.table.update({"restaurant_id": "41704620"},
    # {"$set": {"grades.1.grade": "East 31st Street"}})
    # cli.add_data(a)
    # for i in range(3):
    #     # time.sleep(3)
    #     cli.table.update_many({'ctrlAvailable': 'N'}, {"$set": {"heartBeat": int(time.time()), "gpus.{}.status".format(i): None}}, )
    # cli.table.delete_one({'ctrlAvailable': 'N'})
    cli.table.update_many({}, {"$set": {"heartBeat": int(time.time())}}, )
    # cli.table.update_many({'ctrlAvailable': 'N'}, {"$set": {'gpus.2.status': None}}, )
    # cli.use_gpu_by_num()
    # print(cli.table.find({'ctrlAvailable': 'Y'}))
    # if not list(cli.table.find({'ctrlAvailable': 'Y'})):
    # cli.add_data(a)
    # cli.table.delete_many({"machineID": "_003|_03"})

    gpus = [{"model": "GeForce GTX 1080 Ti", "count": 1},
            {"model": "GeForce GTX 1070 Ti", "count": 5}]
    if cli.compare_gpu(gpus):
        ...
        for i in range(1):
            gp = copy.deepcopy(gpus)
            print(gpus)
            b = cli.chooice_use_gpu_by_num(gp, "TX0010231")
            print(b)
    # while True:
    #     cli.free_gpu_by_task_id("TX0010231")

    cli.insert_update(a)
