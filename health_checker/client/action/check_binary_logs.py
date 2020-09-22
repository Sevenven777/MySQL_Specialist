# -*- coding:UTF-8 -*-
import logging

from health_checker.client.env import Env
from health_checker.client.util import get_disk_capacity

LOG = logging.getLogger(__name__)


class CheckBinaryLogs(object):
    """
    bin_log详解地址：（之后补上）
    """

    def __init__(self, params):
        self.params = params

    def __call__(self):
        """
        二进制日志的主要目的是复制和恢复
        """
        # 单独创建提高可读性
        res = {}
        # 查看是否启用bin_log日志
        res['log_bin'] = Env.database.get_variables_value("log_bin")
        # 如果已经开启二进制日志
        if res['log_bin'] == "ON":

            variables = ['binlog_format', 'sync_binlog', 'expire_logs_days', 'datadir']
            res.update(Env.database.get_multi_variables_value(*variables))
            res['binlog_size'] = Env.database.get_binlog_size()

        # 控制数据库的binlog刷到磁盘上去。 默认，sync_binlog=0，表示MySQL不控制binlog的刷新。
        res['sync_binlog'] = int(res['sync_binlog'])
        # 主要用来控制binlog日志文件保留时间，超过保留时间的binlog日志会被自动删除。
        # expire_logs_days=0：表示所有binlog日志永久都不会失效，不会自动删除；
        res['expire_logs_days'] = int(res['expire_logs_days'])

        # datadir:该参数指定了 MySQL 的数据库文件放在什么路径下。数据库文件即我们常说的 MySQL data 文件。
        # 通过MySQL的变量datadir获取数据盘的路径，再使用psutil获取数据盘的空间
        res['disk_capacity'] = get_disk_capacity(res.pop('datadir'))

        return res
