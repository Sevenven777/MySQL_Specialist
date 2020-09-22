import logging

from health_checker.client.env import Env
from health_checker.client.util import get_disk_capacity

LOG = logging.getLogger(__name__)


class CheckRedoLog(object):
    """
    重做日志。
    确保事务的持久性。
　　 防止在发生故障的时间点，尚有脏页未写入磁盘，在重启mysql服务的时候，根据redo log进行重做，从而达到事务的持久性这一特性。
    """

    def __init__(self, params):
        self.params = params
        self.res = {}

    def __call__(self):
        res = {}
        variables = ['innodb_log_file_size', 'innodb_flush_log_at_trx_commit', 'innodb_flush_method', 'datadir']
        res.update(Env.database.get_multi_variables_value(*variables))

        # datadir:该参数指定了 MySQL 的数据库文件放在什么路径下。数据库文件即我们常说的 MySQL data 文件。
        # 通过MySQL的变量datadir获取数据盘的路径，再使用psutil获取数据盘的空间
        res['disk_capacity'] = get_disk_capacity(res.pop('datadir'))

        # 指定了 InnoDB 在事务提交后的日志写入频率。
        # 当 innodb_flush_log_at_trx_commit 取值为 0 的时候，log buffer 会 每秒写入到日志文件并刷写（flush）到磁盘。但每次事务提交不会有任何影响，也就是 log buffer 的刷写操作和事务提交操作没有关系。在这种情况下，MySQL性能最好，但如果 mysqld 进程崩溃，通常会导致最后 1s 的日志丢失。
        # 当取值为 1 时，每次事务提交时，log buffer 会被写入到日志文件并刷写到磁盘。这也是默认值。这是最安全的配置，但由于每次事务都需要进行磁盘I/O，所以也最慢。
        # 当取值为 2 时，每次事务提交会写入日志文件，但并不会立即刷写到磁盘，日志文件会每秒刷写一次到磁盘。这时如果 mysqld 进程崩溃，由于日志已经写入到系统缓存，所以并不会丢失数据；在操作系统崩溃的情况下，通常会导致最后 1s 的日志丢失。
        # 对于一些数据一致性和完整性要求不高的应用，配置为 2 就足够了；如果为了最高性能，可以设置为 0。有些应用，如支付服务，对一致性和完整性要求很高，所以即使最慢，也最好设置为 1.
        res['innodb_flush_log_at_trx_commit'] = int(res['innodb_flush_log_at_trx_commit'])

        # Redo log的空间通过innodb_log_file_size和innodb_log_files_in_group（默认2）参数来调节。将这俩参数相乘即可得到总的可用Redo log 空间。
        # 多数情况下是通过innodb_log_file_size 来调节。
        # 该参数决定着mysql事务日志文件（ib_logfile0）的大小；
        res['innodb_log_file_size'] = int(res['innodb_log_file_size'])

        return res
