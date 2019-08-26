import requests
import traceback

from .raft_dc import DCSyncObj
from cluster_monitor.utils import (
    common,
    tools
)

if common.vip.ping_vip():
    try:
        res = requests.post(
            url="http://{}:{}/master/api/".format(
                common.CLUSTER_CONF.get('master_host'),
                common.CLUSTER_CONF.get('master_port')
            ),
            headers={
                'agent': common.CLUSTER_CONF.get('agent')
            },
            data={
                'authKey': common.REQ_BASE['req_master']['authKey'],
                'op': 'update_raft_status',
                'raft_op': 'add',
                'raft_addr': common.current_node,
            }
        ).json()
        all_nodes = tools.get_all_nodes_from_raft_status(res)
        RAFT_OBJ = DCSyncObj(common.current_node, all_nodes)
        common.raft_node_enable.is_set()
        common.raft_node_disable.clear()
    except Exception as e:
        tools.logger.warning('{}\n{}'.format(e, traceback.format_exc()))
else:
    common.raft_node_enable.is_set()
    common.raft_node_disable.clear()
    RAFT_OBJ = DCSyncObj(common.current_node, [common.current_node] + common.other_nodes)
