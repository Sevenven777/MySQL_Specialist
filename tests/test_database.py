from health_checker.client.database.mysql import DatabaseManager

d = dict(host="127.0.0.1", user='root', password='123456', size=3, port=3306)
db = DatabaseManager(**d)
print(db.pool)
