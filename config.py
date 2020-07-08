import os
from ssh import *

# ip = "127.0.0.1"
# ip = "93.90.201.35"
host = '0.0.0.0'
domain = "app.faas.ovh"
# config = "..\\config\\app.json"
config_server = os.path.join('..', 'config', 'server.json')
config_app = os.path.join('..', 'config', 'app.json')
Server = getBy(domain, 'domain', config_app)
port = 80
# Server.port
# print(Server)
