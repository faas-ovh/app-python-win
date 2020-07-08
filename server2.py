import jsonify as jsonify
from flask import Flask, stream_with_context, request, Response, render_template, make_response
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


@app.route('/')
@auth.login_required
def index():
    return "Hello, {}!".format(auth.current_user())


@app.route('/test')
@auth.login_required
def test():
    return auth.current_user()

from deploy import *

@app.route('/deploy', methods=['GET', 'POST'])
@auth.login_required
def deploy():
    ## SSH connection
    Server = getBy(getDomain(), 'hostname', config_server)
    client = connect(Server)
    os_ext_script = 'sh'
    # Env List
    result = {}
    list = getEnvList("goethe-pl/app", "goethe-pl/app-python", "python")
    for e in list:
        dict = list[e]
        # print(dict)
        Env = namedtuple("Env", dict.keys())(*dict.values())
        # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
        script = Env.command + '.' + os_ext_script
        template = os.path.join('environment', Env.name, script + '.$')
        scriptpath = os.path.join('environment', Env.name, script)
        createFileFromTemplate(scriptpath, template, {'domain': Env.domain, 'folder': Env.folder, 'github': Env.github})
        bashScript(scriptpath, client)
        result[e] = {Env.name: Env.command}

    list = getEnvProjects("2.faas.ovh", ["install", "start"])
    for e in list:
        dict = list[e]
        # print(dict)
        Env = namedtuple("Env", dict.keys())(*dict.values())
        # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
        script = Env.command + '.' + os_ext_script
        template = os.path.join('environment', Env.name, script + '.$')
        scriptpath = os.path.join('environment', Env.name, script)
        createFileFromTemplate(scriptpath, template, {'folder': Env.folder})
        bashScript(scriptpath, client)
        result[e] = {Env.name: Env.command}

    client.close()
    return {'server': Server.hostname, 'ip': Server.ip, 'result': result}

# pobieranie z git env



@app.route('/template')
@auth.login_required
def template():
    # path = "environment/python/"
    # path = os.path.join('environment', 'python')
    template = os.path.join('environment', 'python', 'install.sh.$')
    newfile = os.path.join('environment', 'python', 'install.sh')
    # document data
    domain = "app.goethe.pl"
    folder = "app.goethe.pl"
    github = "goethe-pl/app"
    vars = {'domain': domain, 'folder': folder, 'github': github}
    text = getTextFromTemplateFile(template, vars)
    createFile(newfile, text)
    return text


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
    return {'environment': request.json['environment'], 'sourcecode': request.json['sourcecode']}


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



def getEnvList2():
    return {
        "0": {
            "name": "python",
            "command": "remove",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
        "1": {
            "name": "python",
            "command": "download",
            "github": "faas-ovh/app-python-win",
            "domain": "2.faas.ovh",
            "folder": "2.faas.ovh"
        },
        "2": {
            "name": "python-static",
            "command": "download",
            # "github": "faas-ovh/www",
            "github": "goethe-pl/app",
            "domain": "2.faas.ovh",
            "folder": "2.faas.ovh"
        },
        "3": {
            "name": "pip",
            "command": "install",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
        "4": {
            "name": "python",
            "command": "install",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
        # "4": {
        #     "name": "copy-folder",
        #     "command": "copy",
        #     "from": "2.faas.ovh"
        #     "to": "2.faas.ovh"
        # },
        "5": {
            "name": "python",
            "command": "start",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
    }


@app.route('/deploy1', methods=['GET', 'POST'])
@auth.login_required
def deploy1():
    domain = "app.faas.ovh"
    Server = getBy(domain, 'hostname', config_server)
    client = connect(Server)

    domain = folder = "api.faas.ovh"

    ## https://github.com/faas-ovh/api
    ## https://github.com/faas-ovh/app-python-win
    # path = "environment\\python\\"
    script = "install.sh"
    template = os.path.join('environment', 'python', script + '.$')
    scriptpath = os.path.join('environment', 'python', script)
    # github = "faas-ovh/api"
    github = "faas-ovh/app-python-win"
    createFileFromTemplate(scriptpath, template, {'domain': domain, 'folder': folder, 'github': github})
    bashScript(scriptpath, client)

    ## https://github.com/faas-ovh/www
    # path = "environment\\python-static\\"
    script = "install.sh"
    template = os.path.join('environment', 'python-static', script + '.$')
    scriptpath = os.path.join('environment', 'python-static', script)
    github = "faas-ovh/www"
    createFileFromTemplate(scriptpath, template, {'domain': domain, 'folder': folder, 'github': github})
    bashScript(scriptpath, client)

    client.close()
    return {'server': Server.hostname, 'ip': Server.ip}


@app.route('/deploy2')
@auth.login_required
def deploy2():
    ip = "93.90.201.35"
    config = "..\\config\\server.json"
    Server = getBy(ip, 'ip', config)
    # print(Server)
    client = connect(Server)

    path = "environment/project\\"
    script = "install.sh"
    template = path + script + ".$"
    scriptpath = path + script
    domain = "app.goethe.pl"
    folder = "app.goethe.pl"
    github = "goethe-pl/app"
    createFileFromTemplate(scriptpath, template, {'domain': domain, 'folder': folder, 'github': github})
    # folder = "api.faas.ovh"
    bashScript(scriptpath, client)
    client.close()
    return {'server': Server.hostname, 'ip': Server.ip}
    # return jsonify({'message': format(auth.current_user())})


# @app.route('/api/secret')
# def api_secret():
#     return jsonify({'message': get_secret_message()})


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
    app.run(host=host, port=port)
