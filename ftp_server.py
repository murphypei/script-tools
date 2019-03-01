from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user(‘upload’, ‘upload’, ‘/data’, perm=‘elradfmwM’)
authorizer.add_user(‘liriwang’, ‘liriwang’, ‘/data/dataset/anon’, perm=‘elradfmwM’)
authorizer.add_anonymous(‘/data/dataset/anon/‘)
handler = FTPHandler
handler.authorizer = authorizer
server = FTPServer((‘’, 21), handler)
server.serve_forever()