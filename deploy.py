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
