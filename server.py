#! /usr/bin/python

import BaseHTTPServer
import hashlib
import base64
import ssl

# Change this:
USER = "admin"
# Generate using SHA256
PASSWORD = "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f"
KEYFILE = "key.key"
CERTFILE = "cert.crt"

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def login(self):
        header = self.headers.getheader("Authorization")
        if header is None:
            return None
        elif not header:
            return False
        auth = header.split()[-1]
        decoded = base64.b64decode(auth).decode("utf-8")
        
        user, pwd = decoded.split(":", 1)
        pwdhash = hashlib.sha256(pwd).hexdigest()
        
        if user == USER and pwdhash == PASSWORD:
            return True
        else:
            return False
    
    def do_GET(self):
        login_status = self.login()
        if login_status is None:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Authorization"')
            self.end_headers()
        elif not login_status:
            self.send_response(403)
            self.end_headers()
        else:
            self.server.conntrack.seek(0)
            connections = self.server.conntrack.read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(connections)

httpd = BaseHTTPServer.HTTPServer(('', 8926), Handler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)
httpd.conntrack = open("/proc/net/ip_conntrack", "rb")
print "Starting Server"
httpd.serve_forever()
