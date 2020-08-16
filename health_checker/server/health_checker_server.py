#!/usr/bin/python
# -*- coding: UTF-8 -*-
from threading import Thread

from health_checker.server.worker import *


class HealthCheckerServer(object):
    """ main class """
    def __init__(self, client):
        self.client = client
        self.workers = []
        for point in ["CheckBinaryLogs", "CheckRedoLog", "CheckConnections", "CheckSafeReplication"]:
            # print("globals", globals())
            # globals() 以字典类型返回当前位置的全部全局变量。
            cls = globals()[point]
            # 参数传递给了GenericWorker
            print(type(globals()[point]))
            print(isinstance(globals()[point], list))
            self.workers.append(cls(self, "catag", point))

        print(self.workers)


    def do_health_check(self):
        """ map """
        # 多线程
        threads = [Thread(target=w.map) for w in self.workers]
        # print(threads)

        # 启动线程
        for thread in threads:
            thread.start()
        # 主线程等待子线程结束
        for thread in threads:
            thread.join()

        first, rest = self.workers[0], self.workers[1:]
        for worker in rest:
            first.reduce(worker)

        self.result = first.rs

    def get_summary(self):
        sum_scores = sum([abs(r.score) for r in self.result])
        mins_scores = sum([abs(r.score) for r in self.result if r.score < 0])

        # print("sum scores : {0}".format(sum_scores))
        # print("mins scores: {0}".format(mins_scores))
        print("您的数据库得分为: {0:.2f}。 总分为100.00分。".format((mins_scores / sum_scores) * 100))
        # print("************************************")
        # print("检查项如下：")
        # for r in self.result:
        #     print(r.name)
        # print("************************************")
        print("给您的数据库参数设置修改建议如下：")
        for r in self.result:
            if r.score < 0:
                print(r.name, r.advise)
