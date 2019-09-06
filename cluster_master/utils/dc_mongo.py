import asyncio
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

from cluster_monitor.utils import common

host_port = common.CLUSTER_CONF.get('mongo_center')
host = host_port.split(':')[0]
port = int(host_port.split(':')[1])
db_name = 'tesra'

connection = MongoClient('mongodb://{}:{}'.format(host, port), connect=False)
db = connection[db_name]
motor_loop = asyncio.new_event_loop()
a_connection = AsyncIOMotorClient(host, int(port), io_loop=motor_loop)
a_db = a_connection[db_name]
