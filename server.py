import jsonify as jsonify
from flask import Flask,  stream_with_context, request, Response, render_template, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from ssh import *
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


# pobieranie z git env


from string import Template

def getTextFromTemplateFile(file, vars):
    # open the file
    filein = open(file)
    # read it
    src = Template(filein.read())
    # do the substitution
    result = src.substitute(vars)
    # result = cf.format(src, title=title, subtitle=sibtitle, list=list)
    # print(result)
    return result

def createFileFromTemplate(newfile, template, vars):
    text = getTextFromTemplateFile(template, vars)
    createFile(newfile, text)

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
    return request.query_string
    # return make_response(jsonify({ 'environment': environment, 'sourcecode': sourcecode }))


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
    template =  os.path.join('environment', 'python', script + '.$')
    scriptpath = os.path.join('environment', 'python', script)
    createFileFromTemplate(scriptpath, template, {'folder': folder})
    bashScript(scriptpath, client)

    client.close()
    return { 'server': Server.hostname, 'ip': Server.ip }


@app.route('/deploy', methods=['GET', 'POST'])
@auth.login_required
def deploy():
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
    return { 'server': Server.hostname, 'ip': Server.ip }

@app.route('/deploy2')
@auth.login_required
def deploy2():
    ip = "93.90.201.35"
    config = "..\\config\\server.json"
    Server = getBy(ip, 'ip', config)
    # print(Server)
    client = connect(Server)

    path = "environment\\python\\"
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
    return { 'server': Server.hostname, 'ip': Server.ip }
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
