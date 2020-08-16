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
        :return:
        """
        # 单独创建提高可读性
        res = {}
        # 查看是否启用bin_log日志
        res['log_bin'] = Env.database.get_variables_value("log_bin")
        # 如果已经开启二进制日志
        if res['log_bin'] == "ON":
            #
            variables = ['binlog_format', 'sync_binlog', 'expire_logs_days', 'datadir']
            res.update(Env.database.get_multi_variables_value(*variables))
            res['binlog_size'] = Env.database.get_binlog_size()

        res['sync_binlog'] = int(res['sync_binlog'])
        res['expire_logs_days'] = int(res['expire_logs_days'])

        res['disk_capacity'] = get_disk_capacity(res.pop('datadir'))

        return res
