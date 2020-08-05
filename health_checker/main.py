#!/usr/bin/python
# -*- coding: UTF-8 -*-
import argparse
import logging.config
import os
import sys
import traceback

# 解决了相对导入包的问题
pkg_root = os.path.realpath(os.path.join(os.path.realpath(__file__),
                                         os.path.pardir,
                                         os.path.pardir))
sys.path.append(pkg_root)

from health_checker.client.env import Env
from health_checker.client.database.mysql import DatabaseManager
from health_checker.client.client import Client
from health_checker.server.health_checker_server import HealthCheckerServer

# 注册日志配置文件
log_cnf = os.path.join(pkg_root, 'conf', 'logging.cnf')
logging.config.fileConfig(log_cnf, disable_existing_loggers=False)
LOG = logging.getLogger(__name__)


def _argparse():
    """
    argument parser
    """
    # 创建一个解析对象
    # description参数用于插入描述脚本用途的信息，可以为空
    parser = argparse.ArgumentParser(description='health checker for MySQL database')
    # add_argument：向该对象中添加要关注的命令行参数和选项
    # --host --user等：选项字符串的名字或列表，例如foo或-fo，--foo
    # action：命令行遇到参数时候的动作，默认为store
    # dest：解析后的参数名称
    parser.add_argument('--host', action='store', dest='host', required=True,
                        help='connect to host')
    parser.add_argument('--user', action='store', dest='user', required=True,
                        help='user for login')
    parser.add_argument('--password', action='store', dest='password',
                        required=True, help='password to use when connecting to server')
    # type：命令行参数应该被转换的类型
    # help：一些帮助信息
    # default：不指定参数时的默认参数
    parser.add_argument('--port', action='store', dest='port', default=3306,
                        type=int, help='port number to use for connection or 3306 for default')
    parser.add_argument('--conn_size', action='store', dest='conn_size', default=5,
                        type=int, help='how much connection for database usage')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    return parser.parse_args()


def main():
    """ entry point """
    try:
        # d = dict(host="127.0.0.1", user='root', password='123456', port=3306, size=3)

        # parser = _argparse()
        # Env.database = DatabaseManager(host=parser.host, user=parser.user, password=parser.password, port=parser.port)

        # 此行是命令行输入的格式
        # python main.py --host 127.0.0.1 --user root --password  123456 --port 3306

        # 可以将此行注释掉，将parser和Env行的注释取消掉，使用命令行输入数据库的参数，由_argparse进行参数解析，再连接数据库
        Env.database = DatabaseManager(host='127.0.0.1', user='root', password='123456', port=3306)

        server = HealthCheckerServer(Client())
        server.do_health_check()
        server.get_summary()

    except Exception as exc:
        print(exc)
        LOG.error(traceback.format_exc())


if __name__ == '__main__':
    main()
