from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse
import cgi
import pprint

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
            pprint.pprint(urlparse.urlparse(self.path))
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
        print form

        # JSon获取post传入的table_id
        # table_id = form.getvalue('tableId')
        # print table_id
        # main_create(table_id)

        self.send_response(200)
        self.end_headers()
        self.wfile.write("Congratulations! Post table id successfully!")


# 启动http服务器，监听9527端口，接受请求url： http://127.0.0.1:9527/table_id
def http_server_run():
    server_ip = '127.0.0.1'
    server_port = 9527
    server_address = (server_ip, server_port)
    http_server = HTTPServer(server_address, HttpServerHanlder)
    print "http server start on {}:{}....".format(server_ip, server_port)
    http_server.serve_forever()


if __name__ == "__main__":

    http_server_run()