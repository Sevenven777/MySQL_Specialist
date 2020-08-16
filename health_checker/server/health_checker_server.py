#!/usr/bin/python
# -*- coding: UTF-8 -*-
from threading import Thread

from health_checker.server.worker import *


class HealthCheckerServer(object):
    """
    main class
    为每一个worker分配一个线程，线程结束以后，再将每一个worker的结果汇总起来（模仿map-reduce架构）
    """
    def __init__(self, client):
        self.client = client
        self.workers = []
        # 简单工厂模式，通过类的名称，从globals函数返回的字典中获得类对象
        for point in ["CheckBinaryLogs", "CheckRedoLog", "CheckConnections", "CheckSafeReplication"]:
            # globals() 以字典类型返回当前位置的全部全局变量。
            cls = globals()[point]
            # 参数传递给了GenericWorker
            # cls()创建一个对象
            self.workers.append(cls(self, "catag", point))

    def do_health_check(self):
        """ map """
        # 多线程
        threads = [Thread(target=w.map) for w in self.workers]

        # 启动线程
        for thread in threads:
            thread.start()
        # 主线程等待子线程结束
        for thread in threads:
            thread.join()

        first, rest = self.workers[0], self.workers[1:]
        # 把所有的结果都添加到first的结果列表中
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
