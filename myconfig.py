import configparser

import os

proDir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(proDir, "myconfig.conf")
path = os.path.abspath(configPath)


class ReadConfig:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.cp.read(path, encoding="utf-8")


rc = ReadConfig()

sqldb = {'host': rc.cp.get("sqldb", "host"),
         'username': rc.cp.get("sqldb", "username"),
         'password': rc.cp.get("sqldb", "password"),
         'database': rc.cp.get("sqldb", "database")}

mgdb = {'host': rc.cp.get("mgdb", "host"),
        'db': rc.cp.get("mgdb", "db")}

api_cfg = rc.cp.get("apicf", "api")

ere_cfg = rc.cp.get("erecf", "api")

my_redis = {'host': rc.cp.get("redis", "host"),
            'password': rc.cp.get("redis", "password"),
            'db': rc.cp.get("redis", "db"),
            'port': rc.cp.get("redis", "port")}

# print(sqldb)
# print(mgdb)
# print(api_cfg
# print(my_redis)


def conf():
    return sqldb, mgdb, api_cfg, ere_cfg, my_redis
