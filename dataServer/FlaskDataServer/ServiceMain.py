from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app

app.run(port=5001, debug=True)
http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5001)
IOLoop.instance().start()
