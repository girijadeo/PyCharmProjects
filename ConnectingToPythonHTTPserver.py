import SimpleHTTPSServerServer
import SimpleWebSocketServer

PORT = 8000

Handler = SimpleHTTPSServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print ("serving at port", PORT)
httpd.serve_forever()