# https://hackersandslackers.com/automate-ssh-scp-python-paramiko/

import paramiko
import json
from collections import namedtuple


def commandList(commands, client):
    result = []
    x=0
    # execute the commands
    for command in commands:
        print("=" * 50, command, "=" * 50)
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(err)
        # x+=1
        # result[x] = stdout
    # return result

def bashScript(filename, client):
    # read the BASH script content from the file
    bash_script = open(filename).read()
    # print("file: ", bash_script, client)
    # execute the BASH script
    stdin, stdout, stderr = client.exec_command(bash_script)
    # read the standard output and print it
    print(stdout.read().decode())
    # print errors if there are any
    err = stderr.read().decode()
    # print(stdin)
    # print(stdout)
    # print(stderr)
    if err:
        print(err)
    # client.close()


def connect(Server):
    # initialize the SSH client
    client = paramiko.SSHClient()
    # add to known hosts
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=Server.ip, username=Server.username, password=Server.password)
        return client
    except:
        print("[!] Cannot connect to the SSH Server")
        exit()


def execScript(client, script):
    # commandList(["pkill apt"], client)
    # commandList(["apt-get install git"], client)

    bashScript(script, client)

    # close the connection


def getClient(hostname, config):
    str = open(config, "r").read()
    dicts = json.loads(str)
    print("if hostname is existing:", hostname)
    for dict in dicts:
        # print(dict)
        Server = namedtuple("Server", dict.keys())(*dict.values())
        print(Server.ip, Server.hostname, Server.os)
        if Server.hostname == hostname:
            print(Server)
            return connect(Server)

    Exception("Server with hostname: " + hostname + " Not Exits")


def getBy(value, name, config):
    str = open(config, "r").read()
    dicts = json.loads(str)
    for dict in dicts:
        print(dict)
        Server = namedtuple("Server", dict.keys())(*dict.values())
        if dict[name] == value:
            return Server
    Exception("Server with hostname: " + value + " Not Exits")
