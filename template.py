import os
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



def createFile(file, text):
    file = open(file, "w")
    file.write(text)
    file.close()


def envTemplate(Env):
    os_ext_script = 'sh'
    script = Env.command + '.' + os_ext_script
    template = os.path.join('environment', Env.name, script + '.$')
    scriptpath = os.path.join('environment', Env.name, script)
    createFileFromTemplate(scriptpath, template, {'folder': Env.folder})
    return scriptpath


def sourcecodeTemplate(Env):
    os_ext_script = 'sh'
    script = Env.command + '.' + os_ext_script
    template = os.path.join('environment', Env.name, script + '.$')
    scriptpath = os.path.join('environment', Env.name, script)
    createFileFromTemplate(scriptpath, template, {'domain': Env.domain, 'folder': Env.folder, 'github': Env.github})
    return scriptpath
