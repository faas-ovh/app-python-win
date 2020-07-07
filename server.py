import jsonify as jsonify
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from ssh import *
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

ip = "127.0.0.1"
config = "..\\config\\app.json"
Server = getBy(ip, 'ip', config)
port = Server.port
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
    path = "environment/python/"
    filename = "install.sh.$"
    template = path + filename
    newfile = path + "install.sh"
    # document data
    domain = "app.goethe.pl"
    folder = "app.goethe.pl"
    github = "goethe-pl/app"
    vars = {'domain': domain, 'folder': folder, 'github': github}
    text = getTextFromTemplateFile(template, vars)
    createFile(newfile, text)
    return text


@app.route('/search', methods=['GET', 'POST'])
@auth.login_required
def search():
    if request.method == 'GET':
        return render_template('search.html')
    else:
        word = request.form['word']
        return word

@app.route('/deploy', methods=['GET', 'POST'])
@auth.login_required
def deploy():
    ip = "93.90.201.35"
    config = "..\\config\\server.json"
    Server = getBy(ip, 'ip', config)
    client = connect(Server)

    ## https://github.com/faas-ovh/api
    path = "environment\\python\\"
    script = "install.sh"
    template = path + script + ".$"
    scriptpath = path + script
    domain = folder = "api.faas.ovh"
    github = "faas-ovh/api"
    createFileFromTemplate(scriptpath, template, {'domain': domain, 'folder': folder, 'github': github})
    bashScript(scriptpath, client)

    ## https://github.com/faas-ovh/www
    path = "environment\\python-static\\"
    script = "install.sh"
    template = path + script + ".$"
    scriptpath = path + script
    domain = folder = "api.faas.ovh"
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
    app.run(host=ip, port=port)
