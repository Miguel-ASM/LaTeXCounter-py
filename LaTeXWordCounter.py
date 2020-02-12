import re
import sys

def ignoreComments(line):
    """
    This function returns the part of the line that it is not commented. A drawback of this implementation is that it removes '\%' from the line
    """
    temp = line.replace(r'\%','')
    cut = temp.find(r'%')
    if cut < 0:
        return temp.strip()
    else:
        return temp[0:cut].strip()

def removeInLineMath(line):
    """
    This function removes the inline math in the string 'line'
    """
    return re.sub( r'\$.*?\$', '', line ).strip()

def removeInLineCommands(line):
    """
    should be called after removeInLineMath
    """
    return re.sub( r'\\\S+\{?.*?\}?', '', line ).strip()


def removeInlineMathAndCommands(line):
    return removeInLineCommands( removeInLineMath( line ) )


def isEnvBegin(line):
    return line.lstrip().startswith(r'\begin')

def isEnvEnd(line):
    return line.lstrip().startswith(r'\end')

def skipEnv(handle):
    recursion = 1 #depth of the environment recursion, if it is 0 whe are outside of all the nested environments

    while recursion > 0:
        line = handle.readline().strip()
        if isEnvBegin(line):
            recursion +=1
        elif isEnvEnd(line):
            recursion -=1
    return




if __name__=='__main__':

    f = open('test.tex','r')
    words = []

    for line in f:
        #ignore the comments
        line = ignoreComments(line)

        #ignore environments
        if isEnvBegin(line):
            skipEnv(f)
        else:
            #remove the equations and commands
            line = removeInlineMathAndCommands(line)

            #add the words to the array words
            words.extend(line.split())

    f.close()
    print(words)
