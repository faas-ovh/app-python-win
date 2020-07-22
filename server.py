import time
import jsonify as jsonify
from flask import Flask, stream_with_context, request, Response, render_template, make_response, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from config import *
from ssh import *
from template import *
import os
import paramiko
import json
from collections import namedtuple
import argparse

import json
from collections import namedtuple

# import sys, getopt
# from basic_auth import app

app = Flask(__name__)
# https://flask-basicauth.readthedocs.io/en/latest/
# If you would like to protect you entire site with basic access authentication, just set BASIC_AUTH_FORCE configuration variable to True:
# app.config['BASIC_AUTH_FORCE'] = True

# context = ('ssl.cert', 'ssl.key')
# hostname = '127.0.0.1'
auth = HTTPBasicAuth()

users = {}
users[Server.username] = generate_password_hash(Server.password)
print(users)


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


from multiprocessing import Process
import threading

import multiprocessing
import time

class processClass:
    client = ''
    command = ''
    folder = ''
    env = ''

    def __init__(self, client, command, folder, env):
        self.client = client
        self.command = command
        self.folder = folder
        self.env = env
        # p = Process(target=self.run, args=())
        # p.daemon = True  # Daemonize it
        # p.start()  # Start the execution
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()

    def run(self):
        #
        # This might take several minutes to complete
        # print(self.command)
        clientCommand(self.client, self.command, self.folder, self.env)
        # time.sleep(10)
        # print("stop")
        # clientCommand(self.client, "stop", self.folder, self.env)
        # p = multiprocessing.Process(target=clientCommand, name="clientCommand", args=(client, key, folder, env))
        # p.start()
        # time.sleep(5)
        # p.terminate()
        # p.join()
        # Start foo as a process
        p = multiprocessing.Process(target=clientCommand, name="clientCommand", args=(self.client, "stop", self.folder, self.env))
        p.start()
        # Wait 10 seconds for foo
        time.sleep(10)
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()
        self.client.close()



# http://localhost/?clone=https://github.com/goethe-pl/app&cmd=start
# http://localhost/?clone=https://github.com/goethe-pl/app&install&start
# http://localhost/?github=goethe-pl/app&install&start
# http://localhost/?start

@app.route('/', methods=['GET'])
@auth.login_required
def index():
    print(request.args)
    folder = domain = "monit.page"

    ## SSH connection
    Server = getBy(domain, 'hostname', config_server)
    client = connect(Server)

    env = 'node'

    # Env List
    result = {
        'sourcecode': {},
        'clone': {},
        'github': {},
        'environment': {},
        'command': {},
        'cmd': {},
        'env': {},
    }

    # if "environment" in request.json:
    #     environment = request.json["environment"]
    #     clientEnvironment(client, environment, folder, result)

    for key in request.args:
        print("==")
        print(key)
        val = request.args[key]
        print(val)

        if key == "github":
            # script = "git --quiet clone git@github.com:" + val + ".git " + folder
            # script = "git clone git@github.com:" + val + ".git " + folder
            script = "git clone https://github.com/" + val + ".git " + folder
            commands = commandList(["ls", script], client)
            result['github'][folder] = commands
            # result['clone'] = clientSourcecode(client, val, folder, result)
            client.close()

        if key == "sourcecode":
            result['sourcecode'] = clientProject(client, folder, result)
            client.close()

        if key == "cmd":
            result['cmd'] = clientCommand(client, val, folder, env)
            client.close()

        if key == "start" or key == "stop" or key == "install" or key == "status":
            result['env'] = clientCommand(client, "stop", folder, env)

            try:
                begin = processClass(client, key, folder, env)
            except:
                # abort(500)
                return redirect("http://" + Server.ip + "/", code=500)

            # result['env'] = clientCommand(client, key, folder, env)
            # return redirect("http://" + Server.ip + "/", code=307)

        if key == "git":
            script = "apt-get install git -y"
            commands = commandList(["ls", script], client)
            result['command'][folder] = commands
            script = "git --version"
            commands = commandList(["ls", script], client)
            result['command'][folder] = commands
            # 'ssh-keygen -R hostname'
            # script = 'if [ ! -n "$(grep "^bitbucket.org " ~/.ssh/known_hosts)" ]; then ssh-keyscan bitbucket.org >> ~/.ssh/known_hosts 2>/dev/null; fi'
            'echo -e "Host github.com\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config'
            script = "ssh-keygen -F github.com || ssh-keyscan github.com >> ~/.ssh/known_hosts"
            commands = commandList(["ls", script], client)
            result['command'][folder] = commands
            client.close()

        time.sleep(1)

    # return {'server': Server.hostname, 'ip': Server.ip, 'result': result, 'param': request.args}
    return redirect("http://" + Server.ip + "/", code=302)


@app.route('/test')
@auth.login_required
def test():
    return "Hello, {}!".format(auth.current_user())
    # return auth.current_user()


from deploy_app import *


# poprzenosic do innego pliku
# stworzyc plik konfiguracyjny: txt/json/yaml/xml
# jaka biblioteka do konwersji pomiedzy formatami? txt/json/yaml/xml
# przeniesienie do apiexec
@app.route('/deploy', methods=['GET', 'POST'])
@auth.login_required
def deploy():
    ## Domain
    print(request.json)
    # folder = domain = "2.faas.ovh"
    if "domain" in request.json:
        folder = domain = request.json["domain"]

        ## SSH connection
        Server = getBy(domain, 'hostname', config_server)
        client = connect(Server)

        if "folder" in Server:
            folder = Server.folder

        print(folder)

        # Env List
        result = {
            'sourcecode': {},
            'environment': {},
            'command': {},
        }

        if "environment" in request.json:
            environment = request.json["environment"]
            result = clientEnvironment(client, environment, folder, result)

        if "sourcecode" in request.json:
            sourcecode = request.json["sourcecode"]
            result = clientSourcecode(client, sourcecode, folder, result)
            result = clientProject(client, folder, result)

        if "command" in request.json:
            command = request.json["command"]
            result = clientCommand(client, command, folder, result)

        client.close()
    return {'server': Server.hostname, 'ip': Server.ip, 'result': result}


def clientEnvironment(client, environment, folder, result):
    print("environment:")
    print(environment)
    list = getEnvProjects("python", folder, ["install"])
    print(list)
    for e in list:
        dict = list[e]
        print(dict)
        Env = namedtuple("Env", dict.keys())(*dict.values())
        scriptpath = envTemplate(Env)
        bashScript(scriptpath, client)
        result['command'][e] = {Env.name: Env.command}
    return result


def clientSourcecode(client, sourcecode, folder, result):
    print("sourcecode:")
    print(sourcecode)
    list = getEnvList(sourcecode, "project", folder, domain)
    print(list)
    for e in list:
        dict = list[e]
        print(dict)
        Env = namedtuple("Env", dict.keys())(*dict.values())
        # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
        scriptpath = sourcecodeTemplate(Env)
        bashScript(scriptpath, client)
        result['sourcecode'][e] = {Env.name: Env.command}

    # print("sourcecode")
    # print(request.json["sourcecode"])
    # list = getGithub(request.json["sourcecode"], "project", domain, folder)
    # for e in list:
    #     dict = list[e]
    #     print(dict)
    #     Env = namedtuple("Env", dict.keys())(*dict.values())
    #     # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
    #     scriptpath = sourcecodeTemplate(Env)
    #     bashScript(scriptpath, client)
    #     result['sourcecode'][e] = {Env.name: Env.command}
    return result


def clientProject(client, folder, result):
    print("project:")
    print(folder)
    list = getEnvProjects("project", folder, ["install", "start"])
    for e in list:
        dict = list[e]
        print(dict)
        Env = namedtuple("Env", dict.keys())(*dict.values())
        # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
        scriptpath = envTemplate(Env)
        bashScript(scriptpath, client)
        result['command'][e] = {Env.name: Env.command}

    print(result)

    # list = getGithub("faas-ovh/www", "project-environment", domain, folder)
    # for e in list:
    #     dict = list[e]
    #     # print(dict)
    #     Env = namedtuple("Env", dict.keys())(*dict.values())
    #     # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
    #     script = Env.command + '.' + os_ext_script
    #     template = os.path.join('environment', Env.name, script + '.$')
    #     scriptpath = os.path.join('environment', Env.name, script)
    #     createFileFromTemplate(scriptpath, template, {'domain': Env.domain, 'folder': Env.folder, 'github': Env.github})
    #     bashScript(scriptpath, client)
    #     result[e] = {Env.name: Env.command}
    return result


def clientCommand(client, command, folder, env):
    print("command:")
    print(command)
    result = {}
    if (command == "install") or (command == "update") or (command == "remove") \
            or (command == "start") or (command == "stop") or (command == "status"):
        print(command)
        # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
        if (command == "start"):
            if (env == 'node'):
                # script = "cd " + folder + " && node server.js"
                script = "cd " + folder + " && sh " + command + ".sh"
            else:
                script = "python3 " + folder + "/app.py 0.0.0.0 80"
        elif (command == "stop"):
            if (env == 'node'):
                # script = 'pkill -f node'
                script = "cd " + folder + " && sh " + command + ".sh"
            else:
                script = "sh " + folder + "/" + command + ".sh"
        else:
            # script = "sh " + folder + "/" + command + ".sh"
            script = "cd " + folder + " && sh " + command + ".sh"

        # script = "cd " + folder + " & ls & " + command + ".sh"
        commands = commandList(["ls", script], client)
        # scriptpath = envTemplate(Env)
        # bashScript(scriptpath, client)
        # result['command'][folder] = {command: script}
        result[folder] = commands
        # result['command'][e] = {Env.name: Env.command, 'commands': commands}
    else:
        result[folder] = {command: "command not recognized"}

    return result


# pobieranie z git env

@app.route('/query', methods=['GET', 'POST'])
@auth.login_required
def query():
    # if request.method == 'GET':
    #     # return render_template('static/index.html')
    #     return app.send_static_file('index.html')
    # else:
    # environment = request.args['environment']
    # sourcecode = request.json['sourcecode']
    # return request.query_string
    # return request.json['environment']
    # return {'environment': request.json['environment'], 'sourcecode': request.json['sourcecode']}
    return {'environment': request.json}


@app.route('/remove', methods=['GET', 'POST'])
@auth.login_required
def remove():
    domain = "app.faas.ovh"
    Server = getBy(domain, 'hostname', config_server)
    client = connect(Server)

    folder = "api.faas.ovh"

    # remove
    # path = "environment\\python\\"
    script = "remove.sh"
    template = os.path.join('environment', 'python', script + '.$')
    scriptpath = os.path.join('environment', 'python', script)
    createFileFromTemplate(scriptpath, template, {'folder': folder})
    bashScript(scriptpath, client)

    client.close()
    return {'server': Server.hostname, 'ip': Server.ip}


def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'

    return resp


if __name__ == '__main__':
    # app.run()
    # main(sys.argv[1:])
    # context = ('ssl.cert', 'ssl.key')
    # app.run(host='0.0.0.0', port=80, ssl_context=context)
    app.run(host=host, port=port, threaded=True)
