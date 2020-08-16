# -*- coding:UTF-8 -*-
import logging
import queue

import MySQLdb
LOG = logging.getLogger(__name__)


class ConnectionPool(object):

    def __init__(self, **kwargs):
        # 连接池支持的连接数
        self.size = kwargs.get('size', 10)
        self.kwargs = kwargs
        # 存放数据库的连接
        self.conn_queue = queue.Queue(maxsize=self.size)
        # 建立好size个与数据库的连接，把这些连接放到队列中
        for i in range(self.size):
            self.conn_queue.put(self._create_new_conn())

    def _create_new_conn(self):
        # 在获取连接阶段起作用
        # 获取MySQL连接是多次握手的结果，除了用户名和密码的匹配校验外，还有IP->HOST->DNS->IP验证，任何一步都可能因为网络问题导致线程阻塞。为了防止线程浪费在不必要的校验等待上，超过connect_timeout的连接请求将会被拒绝。
        # 这里设置了5秒
        return MySQLdb.connect(host=self.kwargs.get('host', '127.0.0.1'),
                               user=self.kwargs.get('user'),
                               passwd=self.kwargs.get('password'),
                               port=self.kwargs.get('port', 3306),
                               connect_timeout=5)

    def _put_conn(self, conn):
        # 使用了queue的put方法，将连接放到队列中，put默认是阻塞调用，非阻塞版本为put_nowait()方法，相当于put(conn, False)
        # 阻塞调用是指：调用返回结果之前，当前线程会被挂起，线程进入非可执行状态，在这个状态下CPU不会给线程分配时间片，线程暂停运行。函数只有在得到结果之后才会返回。
        self.conn_queue.put(conn)

    def _get_conn(self):
        """
        当要连接数据库时，不再创建新的连接，而是之间从队列中获取连接，用完之后再把连接放回队列中，如果获取的连接为空，再新建连接。
        :return: conn
        """
        # get():如果队列为空，get会等待，直到队列里有数据以后再取值，get取值会在队列中移除一个数据，所以当取完连接用完之后，要再使用put方法把连接放回连接池。（get默认为阻塞调用，非阻塞调用方法为get_nowait()）
        # get_nowait()：取值的时候不等待，如果取不到值，程序直接崩溃，所以在获取队列的数据的时候要统一使用get，代码才不会有问题
        # 使用get_nowait()和put_nowait()的时候要做捕获异常处理。
        conn = self.conn_queue.get()
        if conn is None:
            self._create_new_conn()
        return conn

    def exec_sql(self, sql):
        conn = self._get_conn()
        try:
            # 获取连接后，创建游标，使用游标再进行对数据的增删改查。cur执行SQL语句，然后使用fetchall返回所有匹配的每个元素，每个元素作为一个元组组成一个大元组，最后返回的是这一个大元组。
            cur = conn.cursor()
            cur.execute(sql)
            return cur.fetchall()
        # 捕获异常
        except MySQLdb.ProgrammingError as e:
            # 将异常记录到日志中
            LOG.error("execute sql ({0}) error {1}".format(sql, e))
            raise e
        except MySQLdb.OperationalError as e:
            # create connection if connection has interrupted
            conn = self._create_new_conn()
            raise e
        # 无论是正常建立连接执行了SQL语句，还是发生了异常，都要把连接放回到连接队列中去。
        finally:
            self._put_conn(conn)

    def __del__(self):
        # 获取到连接之后用close关闭连接，如果取到的队列中的连接已经为空了，直接pass
        try:
            while True:
                conn = self.conn_queue.get_nowait()
                if conn:
                    conn.close()
        # queue.Empty的作用是，如果队列为空，返回True，如果不为空，返回False
        except queue.Empty:
            pass
