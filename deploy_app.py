from flask import Flask, stream_with_context, request, Response, render_template, make_response
from ssh import *




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


def getEnvProjects(project, folder, commands):
    result = {}
    x = 1
    for cmd in commands:
        result[x] = {
            "name": project,
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

    if "folder" in Server:
        folder = Server.folder

    print(folder)

    # Env List
    result = {
        "sourcecode": {},
        "environment": {},
        "command": {},
    }

    if "environment" in request.json:
        list = getEnvProjects("python", folder, ["install"])
        for e in list:
            dict = list[e]
            print(dict)
            Env = namedtuple("Env", dict.keys())(*dict.values())
            # print(Env.name, Env.command, Env.script, Env.folder, Env.github, Env.domain)
            scriptpath = envTemplate(Env)
            bashScript(scriptpath, client)
            result['command'][e] = {Env.name: Env.command}

    if "sourcecode" in request.json:
        print("sourcecode")
        print(request.json["sourcecode"])
        list = getEnvList(request.json["sourcecode"], "project", folder)
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

        print("project")
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



    client.close()
    return {'server': Server.hostname, 'ip': Server.ip, 'result': result}
