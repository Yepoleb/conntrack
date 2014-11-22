#! /usr/bin/python3

import requests
import socket
from string import ascii_uppercase, digits

URL = "https://192.168.1.1:8926"
# Change this:
AUTH = ("admin", "12345678")

def parse_connection(data):
    connection = {}
    # If a value pair occurs a second time, it gets added here
    connection["response"] = {}
    
    parts = data.split()
    connection["protocol"] = parts[0]
    connection["protocol_num"] = int(parts[1])
    connection["timeout"] = int(parts[2])
    for part in parts[3:]:
        # Example: [ASSURED]
        if part[0] == '[' and part[-1] == ']':
            connection[part[1:-1].lower()] = True
        # Example: ESTABLISHED
        elif all(c in ascii_uppercase+'_' for c in part):
            connection["status"] = part
        # Example: src=192.168.1.150
        elif '=' in part:
            key, value = part.split('=', 1)
            if all(c in digits for c in value):
                value = int(value)
            if not key in connection:
                connection[key] = value
            else:
                connection["response"][key] = value

    return connection

req = requests.get(URL, auth=AUTH, verify=False)
text = req.text

clients = {}
for line in text.splitlines():
    connection = parse_connection(line)
    source = connection["src"]
    # Only count LAN ips
    if not any(source.startswith(p) for p in ("10.", "172.", "192.168.")):
        continue
    if source not in clients:
        clients[source] = 0
    clients[source] += 1

hostnames = {}
socket.setdefaulttimeout(0.1)
for client in clients:
    # Try to get the hostnames of all clients
    try:
        host = socket.gethostbyaddr(client)
        hostnames[client] = host[0]
    except:
        print("Could not resolve hostname for", client)
        hostnames[client] = client

# Sort by connections
for client, count in sorted(clients.items(), key=lambda x: x[1], reverse=True):
    print("[{}]\t{} ({})".format(count, hostnames[client], client))
