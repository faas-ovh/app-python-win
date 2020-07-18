from flask import Flask, stream_with_context, request, Response, render_template, make_response
from ssh import *


def getEnvList(backend, environment, folder, domain):
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
            "domain": domain,
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
