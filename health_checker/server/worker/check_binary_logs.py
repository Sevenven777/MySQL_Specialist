#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

from health_checker.server.worker.generic_worker import GenericWorker
from health_checker.server.worker.advise import Advise
from health_checker.server.util import CheckResult
from health_checker.server.util import humanize_bytes

LOG = logging.getLogger(__name__)


class CheckBinaryLogs(GenericWorker):

    @property
    def action(self):
        return self.__class__.__name__

    def execute(self):
        """
        {'action': 'CheckBinaryLogs',
         'body': {'sync_binlog': 1, 'binlog_format': 'ROW',
         'disk_capacity': 200039985152L, 'log_bin': 'ON', 'expire_logs_days': 7, 'binlog_size': 940841L},
          'is_success': True}
        """
        # 获取客户端传来的信息
        result = self.server.client(action=self.action)
        # 如果**未成功，返回
        if not result.get('is_success'):
            return
        # 如果成功
        else:
            # 得到body信息
            self.body = result.get('body')
            # 查看是否开启log_bin
            log_bin = self.body.get('log_bin')
            # 如果未开启，记录一下
            if log_bin == 'OFF':
                LOG.info("log_bin is OFF, skip {0}".format(self.action))
            # 如果开启了，可以做检查
            else:
                self.do_check()

    def do_check(self):
        self.check_binlog_format()
        self.check_sync_binlog()
        self.check_expire_logs_days()
        self.check_binlog_size()

    def check_binlog_format(self):
        """
        查看binlog日志的格式
        """
        binlog_format = self.body.get('binlog_format')

        # 权重为3
        result = CheckResult.get_result_template(self, CheckResult.high)
        # print(result)
        if binlog_format != 'ROW':
            # 您的配置参数binlog_format设置为{0}，建议设置为'ROW'，否则有主、从数据不一致的风险
            result.advise = Advise.binlog_format_warning.format(binlog_format, 'ROW')
            result.score = -result.score

        self.rs.append(result)

    def check_sync_binlog(self):
        """
        sync_binlog参数来控制数据库的binlog刷到磁盘上去。
        sync_binlog=0，表示MySQL不控制binlog的刷新，由文件系统自己控制它的缓存的刷新。这时候的性能是最好的，但是风险也是最大的。因为一旦系统Crash，在binlog_cache中的所有binlog信息都会被丢失。
        如果sync_binlog>0，表示每sync_binlog次事务提交，MySQL调用文件系统的刷新操作将缓存刷下去。
        sync_binlog=1，表示每次事务提交，MySQL都会把binlog刷下去，是最安全但是性能损耗最大的设置。这样的话，在数据库所在的主机操作系统损坏或者突然掉电的情况下，系统才有可能丢失1个事务的数据。
        """
        sync_binlog = self.body.get('sync_binlog')

        result = CheckResult.get_result_template(self, CheckResult.high)

        if sync_binlog == 0:
            # "您的配置参数sync_binlog设置为{0}，建议设置为1，否则有主、从数据不一致的风险"
            result.advise = Advise.sync_binlog_warning.format(sync_binlog, 1)
            result.score = -result.score

        self.rs.append(result)

    def check_expire_logs_days(self):
        """
        控制binlog日志文件保留时间，超过保留时间的binlog日志会被自动删除。
        """
        expire_logs_days = self.body.get('expire_logs_days')

        result = CheckResult.get_result_template(self, CheckResult.middle)

        # expire_logs_days=0：表示所有binlog日志永久都不会失效，不会自动删除
        if expire_logs_days == 0 or expire_logs_days > 7:
            # "您的配置参数expire_logs_days设置为{0}，建议设置为7，否则存在binlog占用太多磁盘空间的风险"
            result.advise = Advise.expire_binlog_days_warning.format(expire_logs_days, 7)
            result.score = - result.score

        self.rs.append(result)

    def check_binlog_size(self):
        """
        当前系统中的bin log日志总计大小
        """
        binlog_size = self.body.get('binlog_size')
        disk_capacity = self.body.get('disk_capacity')
        percent = 20.0

        result = CheckResult.get_result_template(self, CheckResult.high)

        if binlog_size > disk_capacity * percent / 100:
            # "您的磁盘空间为{0}，您的binlog占用空间为{1}，超过了阈值20%，建议您适当调小expire_logs_days，减少二进制日志保留时间"
            result.advise = Advise.binlog_size_too_large.format(humanize_bytes(disk_capacity),
                                                                humanize_bytes(binlog_size),
                                                                percent)
            result.score = -result.score

        self.rs.append(result)

