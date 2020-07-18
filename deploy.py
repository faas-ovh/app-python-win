from flask import Flask, stream_with_context, request, Response, render_template, make_response
from ssh import *

def getEnvironment():
    return 'python'
    # return request.json['environment']


def getSourcecode():
    return request.json['sourcecode']



def getEnvList(backend, environment, folder):
    return {
        "0": {
            "name": environment,
            "command": "stop",
            "github": "",
            "domain": "",
            "folder": folder
        },
        "1": {
            "name": environment,
            "command": "remove",
            "github": "",
            "domain": "",
            "folder": folder
        },
        "2": {
            "name": environment,
            "command": "download",
            "github": backend,
            "domain": "2.faas.ovh",
            "folder": folder
        },
        # "3": {
        #     "name": "project-static",
        #     "command": "download",
        #     # "github": "faas-ovh/www",
        #     "github": frontend,
        #     "domain": "2.faas.ovh",
        #     "folder": "2.faas.ovh"
        # },
        # "4": {
        #     "name": environment,
        #     "command": "install",
        #     "github": "",
        #     "domain": "",
        #     "folder": "2.faas.ovh"
        # },
    }

def getGithub(github, project, domain, folder):
    return {
        "1": {
            "name": project,
            "command": "download",
            # "github": "faas-ovh/www",
            "github": github,
            "domain": domain,
            "folder": folder
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



# poprzenosic do innego pliku
# stworzyc plik konfiguracyjny: txt/json/yaml/xml
# jaka biblioteka do konwersji pomiedzy formatami? txt/json/yaml/xml
# przeniesienie do apiexec
@app.route('/deploy', methods=['GET', 'POST'])
@auth.login_required
def deploy():
    ## Domain
    print(request.json)
    folder = domain = "2.faas.ovh"
    if "domain" in request.json:
        folder = domain = request.json["domain"]

    ## SSH connection
    Server = getBy(domain, 'hostname', config_server)
    client = connect(Server)
    os_ext_script = 'sh'

    if "folder" in Server:
        folder = Server.folder

    print(folder)

    # Env List
    result = {}
    if "backend" in request.json:
        list = getEnvList(request.json["backend"], "project-backend", folder)
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
        list = getGithub(request.json["frontend"], "project-static", domain, folder)
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
        list = getGithub(request.json["database"], "project-database", domain, folder)
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
        list = getGithub(request.json["sourcecode"], "project", domain, folder)
        for e in list:
            dict = list[e]
            print(dict)
            Env = namedtuple("Env", dict.keys())(*dict.values())
            # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
            script = Env.command + '.' + os_ext_script
            template = os.path.join('environment', Env.name, script + '.$')
            scriptpath = os.path.join('environment', Env.name, script)
            createFileFromTemplate(scriptpath, template, {'domain': Env.domain, 'folder': Env.folder, 'github': Env.github})
            bashScript(scriptpath, client)
            result[e] = {Env.name: Env.command}

    if "environment" in request.json:
        list = getGithub("faas-ovh/www", "project-environment", domain, folder)
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

    # if (domain):
    #     list = getGithub("faas-ovh/www", "project-domain", domain)
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
        list = getGithub("faas-ovh/www", "project-ip", domain)
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
