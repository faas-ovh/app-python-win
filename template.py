
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
