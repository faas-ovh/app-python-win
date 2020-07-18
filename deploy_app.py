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
