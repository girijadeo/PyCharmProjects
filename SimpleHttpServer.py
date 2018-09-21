import socketserver
import http.server

import requests
import multiprocessing

# Variables
PORT = 8000
URL = 'localhost:{port}'.format(port=PORT)

# Setup simple sever
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print ("Serving at port", PORT)
httpd.serve_forever()

httpd.socket.listen(10)
httpd.socket.recv(1032)
httpd.socket.send("hi")

# start the server as a separate process
# server_process = multiprocessing.Process(target=httpd.serve_forever)
# server_process.daemon = True
# server_process.start()

# Getting HTML from the target page
# values = {
#     'name': 'Thomas Anderson',
#     'location': 'unknown'
# }
#
# r = requests.post(URL, data=values)
#
# print(r.text)

# stop the server
# server_process.terminate()