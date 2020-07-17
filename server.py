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

# poprzenosic do innego pliku
# stworzyc plik konfiguracyjny: txt/json/yaml/xml
# jaka biblioteka do konwersji pomiedzy formatami? txt/json/yaml/xml
# przeniesienie do apiexec
@app.route('/deploy', methods=['GET', 'POST'])
@auth.login_required
def deploy():
    ## Domain
    domain = "2.faas.ovh"
    # if (request.json["domain"]):
    print(request.json)
    if "domain" in request.json:
        domain = request.json["domain"]

    ## SSH connection
    Server = getBy(domain, 'hostname', config_server)
    client = connect(Server)
    os_ext_script = 'sh'

    # Env List
    result = {}
    if "backend" in request.json:
        list = getEnvList(request.json["backend"], "project-backend")
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

    if "frontend" in request.json:
        list = getGithub(request.json["frontend"], "project-static", request.json["domain"])
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

    if "database" in request.json:
        list = getGithub(request.json["database"], "project-database", request.json["domain"])
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

    if "sourcecode" in request.json:
        list = getGithub("faas-ovh/www", "project-github", request.json["domain"])
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

    if "environment" in request.json:
        list = getGithub("faas-ovh/www", "project-environment", request.json["domain"])
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

    # if (request.json["domain"]):
    #     list = getGithub("faas-ovh/www", "project-domain", request.json["domain"])
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

    if "ip" in request.json:
        list = getGithub("faas-ovh/www", "project-domain", request.json["domain"])
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

    # list = getEnvProjects(domain, ["stop", "install", "start"])
    list = getEnvProjects(domain, ["install", "start"])
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
    app.run(host=host, port=port)
