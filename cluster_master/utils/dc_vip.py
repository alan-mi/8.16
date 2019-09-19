import IPy
import socket
import random
import psutil
import traceback
from multiprocessing.dummy import Process as Thread
from subprocess import Popen
from scapy.all import (
    conf,
    sendp
)
from scapy.layers.inet import (
    sr1,
    srp,
    Ether,
    ARP,
    IP,
    ICMP
)

from cluster_raft.tools import logger

cluster_config = {
    "master_host": "192.168.137.200",
    "master_port": 8589,
    "slave_port": 8588,
    "agent": "dc_agent",
    "cluster_id": "_001",
    "cluster_name": "ClusterTest",
    "cluster_equipment_number": 38,
    "cluster_status": 0,
    "cluster_created_at": "2019-01-31T11:27:15.850",
    "vip": "192.168.137.200",
    "vip_num": 2,
    "raft_port": 8587,
    "raft_grpc_port": 8586,
    "raft_http_port": 8585,
    "grpc_port": 8590,
    "grpc_port_public": 18590,
    "cluster_server_port": 50050,
    "ai_server_port": 50051,
    "raft_node_offline_limit": 60,
    "raft_leader_interval_hours": 10000,
    "ping_vip_timeout": 1,
    "cluster_lv1_call_center": "47.111.5.37:6001",
    "mongo_center": "47.110.155.194:9000",
    "public_ip": "113.204.194.92",
    "public_port": 18589,
    "arp_cheat_ip": "192.168.137.25",
    "net_address": "192.168.137.0",
    "netmask": "255.255.255.0",
    "net1": "192.168.137.0/24",
    "net2": "192.168.137.0/255.255.255.0",
    "port": 25252,
    "heartbeat": 0.5,
}


conf.verb = 0


class Vip(object):
    def __init__(self):
        self.config = cluster_config
        self.ip = '127.0.0.1'
        self.mac = ''
        self.ether_name = 'lo'
        self.ether_num = self.config.get('vip_num')
        self.ip_mac_dict = {}
        self.vip = self.config.get('vip')
        self.IP = IPy.IP(self.config.get('net2'))
        # self.set_vip('down')
        self._local_ip()
        logger.info('{} {}'.format(self.ip, self.ether_name))

    def _local_ip(self):
        addrs = psutil.net_if_addrs()
        for k, v in addrs.items():
            for v1 in v:
                if v1.family == socket.AF_INET and \
                        v1.address in self.IP and \
                        v1.address != self.vip and \
                        len(addrs[k]) != 1:
                    self.ip = v1.address
                    self.ether_name = k
                    self.mac = list(
                        filter(
                            lambda x: x.family == socket.AF_PACKET,
                            addrs[k]))[0].address
                    break

    def set_vip(self, op, v=True):
        vip = self.check_vip()
        print(vip)
        if op == 'up':
            if vip:
                self.broadcast_vip(v=False)
            else:
                self.clean_local_vip_arp()
                p = Popen('ifconfig {}:{} {} netmask {} {}'.format(
                    self.ether_name,
                    self.ether_num,
                    self.vip,
                    self.config.get('netmask'),
                    op
                ), shell=True)
                p.communicate()
                self.broadcast_vip(v=v)
                if v:
                    logger.info('{} {} {}'.format(
                        traceback.extract_stack()[-2][2], self.vip, op))
        if op == 'down':
            if vip:
                p = Popen('ifconfig {}:{} {} netmask {} {}'.format(
                    self.ether_name,
                    self.ether_num,
                    self.vip,
                    self.config.get('netmask'),
                    op
                ), shell=True)
                p.communicate()
                self.clean_local_vip_arp()
                if v:
                    logger.info('{} {} {}'.format(
                        traceback.extract_stack()[-2][2], self.vip, op))
            else:
                self.clean_local_vip_arp()

    def clean_local_vip_arp(self):
        p = Popen('arp -d {}'.format(
            self.vip,
        ), shell=True)
        p.communicate()

    def check_vip(self):
        addrs = psutil.net_if_addrs()
        for k, v in addrs.items():
            for v1 in v:
                if v1.family == socket.AF_INET and v1.address == self.vip:
                    return k, v1.address, self.mac
        # # getmacbyip() can not be used at the vip(local).
        # mac1 = getmacbyip(self.vip)
        # mac2 = self.mac
        # return mac1 is mac2

    def arp_cheat(self, ip=None):
        sendp(
            Ether(
                src=self.ip_mac_dict.get(self.config.get('arp_cheat_ip')),
                dst=self.mac)
            / ARP(
                hwsrc=self.ip_mac_dict.get(self.config.get('arp_cheat_ip')),
                psrc=self.config.get('arp_cheat_ip'),
                hwdst=self.mac,
                pdst=self.vip,
                op=2
            )
        )
        pass

    def update_ip_mac_maps(self):
        Thread(target=self.update_ip_mac_dict, args=()).start()

    def broadcast_vip(self, v=False):
        sendp(Ether(dst='ff:ff:ff:ff:ff:ff') /
              ARP(hwsrc=self.mac, psrc=self.vip))
        # sendp(Ether(dst=getmacbyip('10.10.2.254'))/ARP(
        #     hwsrc=self.mac,
        #     psrc=self.vip,
        #     hwdst=getmacbyip('10.10.2.254'),
        #     pdst='10.10.2.254',
        #     op=2
        # ))
        # sendp(Ether(dst=getmacbyip('10.10.2.1'))/ARP(
        #     hwsrc=self.mac,
        #     psrc=self.vip,
        #     hwdst=getmacbyip('10.10.2.1'),
        #     pdst='10.10.2.1',
        #     op=2
        # ))
        if v:
            logger.info('{}: {} - {}'.format(self.vip, self.mac, self.ip))

    def update_ip_mac_dict(self):
        self.ip_mac_dict = {}
        ans, unans = srp(Ether(dst="FF:FF:FF:FF:FF:FF") /
                         ARP(pdst=self.config.get('net1')), timeout=1)
        self.ip_mac_dict.update(
            {rcv.sprintf("%ARP.psrc%"): rcv.sprintf("%Ether.src%") for snd, rcv in ans})

    def ping_vip(self):
        vip_packet = IP(dst=self.vip, ttl=64, id=random.randint(1, 65535)) / \
            ICMP(id=random.randint(1, 65535), seq=random.randint(1, 65535)) / b''
        ping_vip = sr1(
            vip_packet,
            timeout=self.config.get('ping_vip_timeout'),
            verbose=False)
        logger.info('check vip online status:{}'.format(ping_vip))
        if ping_vip:
            return True
        else:
            return False


vip = Vip()
if __name__ == '__main__':
    vip.set_vip("up",True)