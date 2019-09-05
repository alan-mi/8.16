import random
import datetime
from sqlalchemy import (
    DateTime,
    Integer,
    Boolean
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, String, Column


from cluster_monitor.utils import common


Base = declarative_base()


class SqliteDB(object):
    def __init__(self):
        self.engine = create_engine(
            'sqlite:///{}/db.sqlite3'.format(common.PROJECT_HOME))
        self.tables = {
            'cluster_master_machinestatus': MachineStatus,
            'cluster_slave_localhoststatus': LocalhostStatus,
        }
        self.session = sessionmaker(bind=self.engine, autoflush=True)()
        # self.session.query(self.tables.get('cluster_master_machinestatus')).filter().first()
        # self.session.merge(MachineStatus(
        #     host_port='10.10.2.100:8801',
        #     is_online=False,
        #     create_time=datetime.datetime.now(),
        #     last_online_time=datetime.datetime.now(),
        #     update_time=datetime.datetime.now()
        # ))
        # self.session.commit()
        # self.session.close()

    def commit(self, Obj):
        self.session.merge(Obj)
        self.session.commit()

    def close(self):
        self.session.close()

    def shuffle_candidate(self):
        table_class = self.tables.get('cluster_master_machinestatus')
        available_list = self.session.query(
            table_class).filter(table_class.is_online).all()
        order_list = list(range(len(available_list)))
        random.shuffle(order_list)
        for i, o in zip(order_list, available_list):
            o.candidate_order_num = i
            self.commit(o)
        return len(order_list)

    def get_candidate(self):
        table_class = self.tables.get('cluster_master_machinestatus')
        return self.session.query(table_class).filter_by(host_port='{}:{}'.format(
            common.vip.ip, common.CLUSTER_CONF.get('slave_port')), is_online=True).first()

    def get_master_db_info(self):
        table_class = self.tables.get('cluster_master_machinestatus')
        return list(self.session.query(table_class).all())


class MachineStatus(Base):
    __tablename__ = 'cluster_master_machinestatus'
    host_port = Column(String(25), primary_key=True, nullable=False)
    is_online = Column(Boolean(), nullable=False)
    create_time = Column(DateTime(), nullable=False)
    last_online_time = Column(DateTime(), nullable=False)
    update_time = Column(DateTime(), nullable=False)
    candidate_order_num = Column(Integer(), nullable=False)


class LocalhostStatus(Base):
    __tablename__ = 'cluster_slave_localhoststatus'
    host_port = Column(String(25), primary_key=True, nullable=False)
    check_time = Column(DateTime(), nullable=False)
    cpu_count = Column(Integer(), nullable=False)


if __name__ == '__main__':
    sqlite_obj = SqliteDB()
