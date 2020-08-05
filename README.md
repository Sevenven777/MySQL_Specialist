# MySQL数据库专家系统

这是一个MySQL数据库专家系统，可以为你的数据库进行打分，并给出具体的意见和建议。

可选由命令行输入参数，现在的系统改成了直接执行main.py就可以获得检查结果。

test下的文件可以测试数据库的连接。
test.py由命令行输入参数，测试系统是否能正常运行，命令行输入参数的格式已经写在代码中。

现有的检查项有：
- CheckBinaryLogs
    - check_binlog_format
    - check_sync_binlog
    - self.check_expire_logs_days
    - self.check_binlog_size
- CheckRedoLog
    - check_innodb_flush_log_at_trx_commit
    - check_flush_method
    - check_redo_log_file_size
- CheckConnections
    - check_max_connections

可以根据advise中的建议再添加新的检查项。

运行后输出如下：
> 您的数据库得分为: 29.41。 总分为100.00分。
> 给您的数据库参数设置修改建议如下：
> CheckBinaryLogs 您的配置参数expire_logs_days设置为0，建议设置为7，否则存在binlog占用太多磁盘空间的风险
> CheckConnections 数据库连接数过多容易造成线程频繁的上下文切换，连接数过少不能充分发挥数据库的性能，您的数据库连接数是151，你的buffer pool大小是8.00 MB，建议您的数据库连接数设置在1~3范围内，也可以直接设置为2

因为还没有前端页面，所有信息的输出用的暂时是print。