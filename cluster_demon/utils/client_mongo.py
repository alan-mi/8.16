# coding:utf-8
import time
from datetime import datetime

import pymongo
import collections


class Mongo:
    def __init__(self, host, port, db, table):
        self.client = pymongo.MongoClient(host='192.168.137.2', port=27017)
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
        rule.update({"heartBeat": {"$gte": int(time.time()) - 5}})
        print(rule)
        machines = self.find_data(rule)
        return machines

    def free_gpu_by_task_id(self, task_id):
        """
        释放gpu
        :param task_id: 任务id
        :return: None
        """
        rule = {'ctrlAvailable': 'N', "gpus.status": task_id}
        for task in cli.find_data(rule):
            for gpu in task["gpus"]:
                if gpu["status"] == task_id:
                    gpu["status"] = None
            print(task)
            cli.table.update(rule, task)

    def use_gpu_by_num(self):
        res = self.table.aggregate(
            [{"$match": {"heartBeat": {"$gte": int(time.time()) - 5}, "gpus.status": None}},
             {"$project": {"gpus": 1, "_id": 0}},
             {"$unwind": "$gpus"}])
        it = [gpu["gpus"]["model"] for gpu in res if not gpu["gpus"]["status"]]
        all_gpu = collections.Counter(it)
        return all_gpu

    def chooice_use_gpu_by_num(self, need_gpus, task_id):
        task = {}
        mac = {}
        for model in need_gpus:
            rule = {"heartBeat": {"$gte": int(time.time()) - 5}, "gpus.status": None}
            res = self.table.find(rule)
            for machine in res:
                for gpu in machine["gpus"]:
                    if gpu.get("model") == model["model"] and not gpu.get("status") and model["count"]>0:
                        model["count"] -= 1
                        gpu["status"] = task_id
                        if not mac.get(machine["machineID"]) :
                            mac[machine["machineID"]] = [gpu["id"]]
                        else:
                            mac[machine["machineID"]].append(gpu["id"])
                self.table.update({"machineID": machine["machineID"]}, machine)
        task["taskID"] = task_id
        task["machines"] = mac
        return task

    def compare_gpu(self,gpus):
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
        if not self.table.find_one({"machineID": machine["machineID"]}):
            self.add_data(machine)
        self.table.update_one({"machineID": machine["machineID"]}, {"$set": {"heartBeat": int(time.time())}})


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
    "heartBeat": int(time.time())
}

cli = Mongo(host='192.168.137.2', port=27017, db="cluster", table="machines")

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
    cli.add_data(a)
    for i in range(3):
        cli.table.update_many({'ctrlAvailable': 'N'}, {"$set": {"heartBeat": int(time.time()), "gpus.{}.status".format(i): None}}, )
    # cli.table.delete_one({'ctrlAvailable': 'N'})
    # cli.table.update_many({'ctrlAvailable': 'N'}, {"$set": {"heartBeat": int(time.time())}}, )
    # cli.use_gpu_by_num()
    # print(cli.table.find({'ctrlAvailable': 'Y'}))
    # if not list(cli.table.find({'ctrlAvailable': 'Y'})):
    # cli.add_data(a)
    # cli.table.delete_many({"machineID": "_003|_03"})

    # gpus = [{"model": "GeForce GTX 1080 Ti", "count": 1}, {"model": "GeForce GTX 1070 Ti", "count": 1}]
    # if cli.compare_gpu(gpus):
    #     print(cli.chooice_use_gpu_by_num(gpus, "TX0010231"))
