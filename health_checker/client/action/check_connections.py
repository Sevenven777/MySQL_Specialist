# -*- coding:UTF-8 -*-
import logging

from health_checker.client.env import Env

LOG = logging.getLogger(__name__)


class CheckConnections(object):

    def __init__(self, params):
        self.params = params

    def __call__(self):
        res = Env.database.get_multi_variables_value('max_connections', 'innodb_buffer_pool_size')

        # 同时连接客户端的最大数量
        res['max_connections'] = int(res['max_connections'])
        """
        该参数定义了 InnoDB 存储引擎的表数据和索引数据的最大内存缓冲区大小。和 MyISAM 存储引擎不同，MyISAM 的 key_buffer_size只缓存索引键， 而 innodb_buffer_pool_size 却是同时为数据块和索引块做缓存，这个特性和 Oracle 是一样的。这个值设得越高，访问 表中数据需要的磁盘 I/O 就越少。
        InnoDB缓存池缓存索引、行的数据、自适应哈希索引、插入缓存（Insert Buffer）、锁 还有其他的内部数据结构。（所以，如果数据库的数据量不大，并且没有快速增长，就不必为缓存池分配过多的内存，当为缓存池配置的内存比需要缓存的表和索引大很多也没什么必要，会造成资源浪费。）
        """
        res['innodb_buffer_pool_size'] = int(res['innodb_buffer_pool_size'])

        return res
