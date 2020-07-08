from flask import Flask, stream_with_context, request, Response, render_template, make_response
from ssh import *

def getEnvironment():
    return 'python'
    # return request.json['environment']


def getSourcecode():
    return request.json['sourcecode']


def getDomain():
    return "2.faas.ovh"
    # return request.json['domain']

def getEnvList(frontend, backend, environment):
    return {
        "0": {
            "name": "project",
            "command": "stop",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
        "1": {
            "name": "project",
            "command": "remove",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
        "2": {
            "name": "project",
            "command": "download",
            "github": backend,
            "domain": "2.faas.ovh",
            "folder": "2.faas.ovh"
        },
        "3": {
            "name": "project-static",
            "command": "download",
            # "github": "faas-ovh/www",
            "github": frontend,
            "domain": "2.faas.ovh",
            "folder": "2.faas.ovh"
        },
        "4": {
            "name": environment,
            "command": "install",
            "github": "",
            "domain": "",
            "folder": "2.faas.ovh"
        },
    }

def getEnvProjects(folder, commands):
    result = {}
    x=1
    for cmd in commands:
        result[x] = {
            "name": "project",
            "command": cmd,
            "folder": folder
        }
        x += 1
    # print(result)
    return result

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
