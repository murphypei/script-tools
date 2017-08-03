# -*- coding:utf-8 -*-

__author__ = 'itachi'


import pprint
import random

import yaml
import redis
import mysql.connector
from mysql.connector import errorcode

# 编码转换，我电脑有作用，别的不知道，编码问题太复杂了！！！
import sys 
reload(sys) 
sys.setdefaultencoding("utf-8")

# 随机端口号生成、检查和存储
def random_port_generator(redis_info, num_cnt=3): # 默认返回三个端口号
    
    # 特殊端口set
    special_port = set(['8080', '3306', '6379'])
    
    # 端口范围
    min_range = 1025    
    max_range = 65534  

    # 连接redis数据库
    r = redis.Redis(host=redis_info['host'], port=redis_info['port'], db=redis_info['db']) 
    # 获取通过键来获取集合
    usedport = r.smembers('usedport')   # 在redis中存储键为usedport的集合，集合的元素是使用过的端口号的字符串形式

    results = []
    i = 0
    while i < num_cnt:
        # 生成一个指定范围的随机整数
        n = random.randint(min_range, max_range)
        # 如果随机数的字符串形式不在两个集合中，则有效
        if str(n) not in (usedport | special_port):
            results.append(n)           # 将生成的整数加入结果中
            special_port.add(str(n))        # 整数的字符串形式加入集合中
            i += 1
        else:
            continue
    
    # 将这些数存回数据库
    for port in special_port:
        r.sadd('usedport', port)

    # 返回端口
    return tuple(results)


def create_yaml(mysql_info, redis_info, table_id):

    try:
        cnx = mysql.connector.connect(
                user=mysql_info['username'],
                password=mysql_info['passwd'],
                host=mysql_info['host'],
                database=mysql_info['db_name'],
                port=mysql_info['port'])      
        
        mysql_cursor = cnx.cursor()

    # 异常处理
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database is not exist")
        else:
            print(err)
        
        mysql_cursor.close()
        exit("MySQL connect failed")
    
    # 获取随机端口
    random_port = random_port_generator(redis_info)

    # 以字典的形式来生成yaml文件
    yaml_dict = {}
    yaml_dict['version'] = "3"
    yaml_dict['services'] = {}
    yaml_dict['services']['volumes'] = {}

    # 查询cs_application表，获取project_name
    sql_str = 'SELECT `project_name` FROM `cs_application` WHERE table_id="{}"'.format(table_id)
    mysql_cursor.execute(sql_str)
    result = mysql_cursor.fetchone()
    if result is None:
        exit("Query project name failed.")
    project_name = result[0]
    yaml_dict['services']['networks'] = {project_name: None}

    # 查询cs_database表
    fields = ['root_password', 'database_password', 'database_name', 'database_account', 'database_id']
    sql_str = 'SELECT `{fields[0]}`, `{fields[1]}`, `{fields[2]}`, `{fields[3]}`, `{fields[4]}` from `cs_database` WHERE `table_id`="{id}"'.format(fields=fields, id=table_id)
    mysql_cursor.execute(sql_str)
    result = mysql_cursor.fetchall()
    for r in result:
        
        data = dict(zip(fields, r))
        # pprint.pprint(data)

        # 组装要生成yaml中mysql部分的键值map
        mysql_dict = {u'{}-mysql{}'.format(project_name, data['database_id']): {
            'image': 'mysql',
            'ports': ['{}:3306'.format(random_port[0])],
            'deploy': {
                'placement': {
                    'constraints': "[ node.labels.cluster == database{} ]".format(random.randint(12,14))
                    },   # database_num 是一个随机数
                'replicas': 1,
                'restart_policy': {
                    'condition': 'any'
                    }
            },
            'environment': {
                'MYSQL_DATABASE': data['database_name'],
                'MYSQL_PASSWORD': data['database_password'],
                'MYSQL_ROOT_PASSWORD': data['root_password'],
                'MYSQL_USER': data['database_account'],
            },
            'networks': [project_name],
            'volumes': ['mysql_data{}:/var/lib/mysql'.format(data['database_id'])]
            }
        }

        # pprint.pprint(mysql_dict)
        k, v = mysql_dict.popitem()
        yaml_dict['services'][k] = v
        yaml_dict['services']['volumes']['mysql_data{}'.format(data['database_id'])] = None
        
    # 组装要生成yaml中redis部分的键值map
    redis_dict = {'redis': {
        'image': 'redis',
        'ports': ['{}:6379'.format(random_port[1])],
        'deploy': {
            'placement': {'constraints': "[ node.labels.cluster == app ]"},
            'replicas': 1,
            'restart_policy': {'condition': 'any'}
        },
        'networks': [project_name]
        }
    }
    k, v = redis_dict.popitem()
    yaml_dict['services'][k] = v


    # 查询cs_subproject表
    fields = ['subproject_name', 'subproject_port', 'subproject_id', 'persistent_folder_path', 'persistent_need']
    sql_str = 'SELECT `{fields[0]}`, `{fields[1]}`, `{fields[2]}`, `{fields[3]}`, `{fields[4]}` from `cs_subproject` WHERE `table_id`="{id}"'.format(fields=fields, id=table_id)
    mysql_cursor.execute(sql_str)
    result = mysql_cursor.fetchall()

    for r in result:
        
        data = dict(zip(fields, r))
        # pprint.pprint(data)
        
        # 组装要生成yaml中subproject部分的键值map
        sub_project_dict = {u'{0}{1}'.format(data['subproject_name'], data['subproject_id']): {
            'image': u'gitlab-yfy.nj-itc.com.cn:4000/root/{0}:{1}-latest'.format(project_name, data['subproject_name']),
            'ports': ['{0}:{1}'.format(random_port[2], data['subproject_port'])],
            'volumes': ['data{0}:{1}'.format(data['subproject_id'], data['persistent_folder_path'])],
            'logging': {
                'driver': 'gelf',
                'options': {
                    'gelf-address': "udp://192.168.21.2:12201",
                    'tag': data['subproject_name']
                },
            },
            'deploy': {
                'replicas': 1,
                'restart_policy': {
                    'condition': 'any'
                    },
            },
            'networks': [project_name]
            }
        }

        
        # 判断持久化
        if data['persistent_need'] == 0:
            print "******"
            del sub_project_dict[u'{0}{1}'.format(data['subproject_name'], data['subproject_id'])]['volumes']
        k, v = sub_project_dict.popitem()
        yaml_dict['services'][k] = v
        if data['persistent_need'] != 0:
            print "###"
            yaml_dict['services']['volumes']['data{}'.format(data['subproject_id'])] = None

    
    #pprint.pprint(yaml_dict)
    # dump 到文件中
    with open('compose.yml', 'w') as fout:
        yaml.dump(yaml_dict, fout, allow_unicode=True, encoding=('utf-8'), default_flow_style=False)
    
    mysql_cursor.close()
    
if __name__ == "__main__":
    
    table_id = 6402025537844
    mysql_info = {'host':'192.168.191.130', 'port':3306, 'username':'root', 'passwd':'admin', 'db_name':'wex5'}
    redis_info = {'host': '192.168.191.130', 'port':6379, 'db':0}
    create_yaml(mysql_info, redis_info, table_id)
