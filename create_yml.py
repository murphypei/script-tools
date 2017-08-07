# -*- coding:utf-8 -*-


import pprint
import random
import os
import yaml
import redis
import mysql.connector
from mysql.connector import errorcode

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse
import cgi

# 编码转换
import sys 
reload(sys)
sys.setdefaultencoding("utf-8")

usedport = set()
special_port = set(['8080', '3306', '6379'])
generate_port = []

# 首先获取Redis数据库中已经使用端口
def get_uesdports(redis_info):
    
    # 连接redis数据库
    r = redis.Redis(host=redis_info['host'], port=redis_info['port'], db=redis_info['db']) 
    # 获取通过键来获取集合
    global usedport
    usedport = r.smembers('usedport')   # 在redis中存储键为usedport的集合，集合的元素是使用过的端口号的字符串形式


# 将special_port写入redis
def save_special_ports(redis_info):
    
    # 连接redis数据库
    r = redis.Redis(host=redis_info['host'], port=redis_info['port'], db=redis_info['db']) 
    # 将这些数存回数据库
    for port in special_port:
        r.sadd('usedport', port)


# 随机生成一个端口号
def random_port_generator():
    
    # 端口范围
    min_range, max_range = 1025, 65534
    global generate_port
    while(True):
        n = random.randint(min_range, max_range)
        # 如果随机数的字符串形式不在两个集合中，则有效
        if str(n) not in (usedport | special_port):               
            special_port.add(str(n))        # 整数的字符串形式加入集合中
            generate_port.append(n)
            return n                        # 返回端口


#生成配置文件
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
        
        exit("MySQL connect failed")

    # 只需要调用一次从redis获取usedport
    get_uesdports(redis_info)  

    # 以字典的形式来生成yaml文件
    yaml_dict = {}
    # yaml_dict['version'] = "3"
    yaml_dict['services'] = {}
    yaml_dict['volumes'] = {}
    #yaml_dict['services']['volumes'] = {}

    # 查询cs_application表，获取project_name
    sql_str = 'SELECT `project_name` FROM `cs_application` WHERE table_id="{}"'.format(table_id)
    mysql_cursor.execute(sql_str)
    result = mysql_cursor.fetchone()
    #print result[0].decode('gbk').encode('utf8')

    if result is None:
        exit("Query project name failed.")
    project_name = result[0]
    yaml_dict['networks'] = {project_name: None}
    #yaml_dict['services']['networks'] = {project_name: None}

    # 查询cs_database表
    fields = ['root_password', 'database_password', 'database_name', 'database_account', 'database_id']
    sql_str = 'SELECT `{fields[0]}`, `{fields[1]}`, `{fields[2]}`, `{fields[3]}`, `{fields[4]}` from `cs_database` WHERE `table_id`="{id}"'.format(fields=fields, id=table_id)
    mysql_cursor.execute(sql_str)
    result = mysql_cursor.fetchall()

    database_result_size = len(result)
    database_num = []

    for r in result:
        
        data = dict(zip(fields, r))
        # pprint.pprint(data)

        # 组装要生成yaml中mysql部分的键值map
        num = random.randint(12, 14)
        database_num.append(num)

        mysql_dict = {u'{}-mysql{}'.format(project_name, data['database_id']): {
            'image': 'mysql',
            'ports': ['"{}:3306"'.format(random_port_generator())],
            'deploy': {
                'placement': {
                    'constraints': "[ node.labels.cluster == database{} ]".format(num)
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
            'volumes': ['"mysql_data{}:/var/lib/mysql"'.format(data['database_id'])]
            }
        }

        # pprint.pprint(mysql_dict)
        k, v = mysql_dict.popitem()
        yaml_dict['services'][k] = v
        yaml_dict['volumes']['mysql_data{}'.format(data['database_id'])] = None
        
    # 组装要生成yaml中redis部分的键值map
    redis_dict = {'redis': {
        'image': 'redis',
        'ports': ['"{}:6379"'.format(random_port_generator())],
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
    sql_str = 'SELECT `{fields[0]}`, `{fields[1]}`, `{fields[2]}`, `{fields[3]}`, `{fields[4]}`' \
              'from `cs_subproject` WHERE `table_id`="{id}"'.format(fields=fields, id=table_id)
    mysql_cursor.execute(sql_str)
    result = mysql_cursor.fetchall()

    for r in result:
        
        data = dict(zip(fields, r))
        # pprint.pprint(data)
        # 组装要生成yaml中subproject部分的键值map
        sub_project_dict = {u'{0}{1}'.format(data['subproject_name'], data['subproject_id']): {
            'image': u'gitlab-yfy.nj-itc.com.cn:4000/root/{0}:{1}-latest'.format(
                project_name, data['subproject_name']),
            'ports': ['"{0}:{1}"'.format(random_port_generator(), data['subproject_port'])],
            'volumes': ['"data{0}:{1}"'.format(data['subproject_id'], data['persistent_folder_path'])],
            'logging': {
                'driver': '"gelf"',
                'options': {
                    'gelf-address': '"udp://192.168.21.2:12201"',
                    'tag': data['subproject_name']
                },
            },
            'deploy': {
                'placement': {
                    'constraints': "[ node.labels.cluster == app{} ]".format(random.randint(1,5))
                    },
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
            del sub_project_dict[u'{0}{1}'.format(
                data['subproject_name'], data['subproject_id'])]['volumes']
        k, v = sub_project_dict.popitem()
        yaml_dict['services'][k] = v
        if data['persistent_need'] != 0:
            print "###"
            yaml_dict['volumes']['data{}'.format(data['subproject_id'])] = None

    
    #pprint.pprint(yaml_dict)
    # dump 到文件中
    with open('tmp.yml', 'w') as fout:
        fout.write('version: "3"\n'.encode('utf-8'))
        yaml.safe_dump(yaml_dict, fout, allow_unicode=True, encoding=('utf-8'),
                  default_flow_style=False, default_style=None)
        fout.flush()
       

    with open('tmp.yml', 'r') as fin:
        with open('compose.yml', 'w') as fout:
            fr = fin.read()
            fr = fr.replace("'", "")
            fr = fr.replace(" - ", "   - ")
            fr = fr.replace("null", "")
            fout.write(fr)
            fout.flush()

    save_special_ports(redis_info)   # 只需要用完了一次写回数据库中
    mysql_cursor.close()

    print "create_yml return: generate_port: ", generate_port
    return database_result_size, database_num


# 执行系统命令，返回执行结果
def execute_sys_cmd(cmd):
    result = os.popen(cmd).readlines()
    return result


#数据写入数据库
def put_mysql_data(database_result_len, database_num, table_id):

    # 连接mysql
    try:
        cnx = mysql.connector.connect(
            user='root',
            password='x5',
            host='127.0.0.1',
            database='wex5',
            charset='utf8', )  # 指定数据库名为yaml
        mysql_cursor = cnx.cursor()

        if database_num == 12:
            database_ip = '192.168.21.14'
        elif database_num == 13:
            database_ip = '192.168.21.15'
        else:
            database_ip = '192.168.21.16'

        print generate_port

        for i in range(database_result_len):
            mysql_cursor.execute(
                "UPDATE `cs_database` SET" \
                " `pass_database_port` = '{0}'," \
                " `pass_database_ip_port` = '{1}',"\
                "`pass_database_ip` = '{2}'" \
                " WHERE `table_id` ='{3}' and `database_id` = '{4}'".format(
                    generate_port[i],
                    database_num[i],
                    database_ip,
                    table_id,
                    i+1))

        mysql_cursor.execute(
            "UPDATE `cs_application` SET `project_mapping_port` = '{}'" \
            "where `table_id` = '{}'".format(
                generate_port[database_result_len], table_id))

        for j in range(database_result_len+1, len(generate_port)):
            mysql_cursor.execute(
                "UPDATE `cs_subproject` SET `subject_mapping_port` = '{}'" \
                "WHERE `table_id` = '{}' AND `subproject_id` = '{}'".format(
                    generate_port[j], table_id,  j - database_result_len))

        cnx.commit()

    finally:
        # 关闭数据库连接
        cnx.close()

def main_create(table_id):

    host = "127.0.0.1"
    mysql_info = {'host':host, 'port':3306, 'username':'root', 'passwd':'x5', 'db_name':'wex5'}
    redis_info = {'host': host, 'port':6379, 'db':0}
    database_len, database_num = create_yaml(mysql_info, redis_info, table_id)
    put_mysql_data(database_len, database_num, table_id)


# Http服务器请求处理
class HttpServerHanlder(BaseHTTPRequestHandler):
    # 传入参数的页面
    post_page = \
        """
        <html>
        <body>
            <form enctype="multipart/form-data" action="/create_yml" method="post">
                <input type="hidden" name="token" value="upload-token"/>
                table_id:
                <input type="text" name="tableId" />
                <input type="submit" value="Submit" />
            </form>
        </body>
        </html>
        """

    def do_GET(self):
        print "This is a get request..."
        if self.path != '/table_id':
            self.send_error(404, "File not found.")
            return
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(self.post_page)))
            self.end_headers()
            self.wfile.write(self.post_page)
        # 只接受 "/table_id"的路径请求


    def do_POST(self):
        print "This is a post request..."
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        # 获取post传入的table_id
        table_id = form.getvalue('tableId')
        main_create(table_id)

        self.send_response(200)
        self.end_headers()
        self.wfile.write("Congratulations! Post table id successfully!")


# 启动http服务器，监听9527端口，接受请求url： http://127.0.0.1:9527/table_id
def http_server_run():
    server_ip = '127.0.0.1'
    server_port = 9527
    server_address = (server_ip, server_port)
    http_server = HTTPServer(server_address, HttpServerHanlder)
    print "http server start...."
    http_server.serve_forever()


if __name__ == "__main__":

    host = "192.168.191.130"
    table_id = 6402025537844
    mysql_info = {'host':host, 'port':3306, 'username':'root', 'passwd':'admin', 'db_name':'wex5'}
    redis_info = {'host': host, 'port':6379, 'db':0}
    database_len, database_num = create_yaml(mysql_info, redis_info, table_id)
