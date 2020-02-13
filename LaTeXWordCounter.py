import re
import sys
from matplotlib import pyplot as plt


# Auxiliar Methods

def ignoreComments(line):
    """
    This function returns the part of one line string 'line' that it is not commented.
    A drawback of this implementation is that it removes '\%' from the line.

    Examples:

    - line = r'%This line starts with a comment'

        ignoreComments(line) ---> ''

    - line = r'There is a %comment in the middle'

        ignoreComments(line) ---> 'There is a '

    - line = r'Percentage \% symbols are not respected %this is ignored'

        ignoreComments(line) ---> 'Percentage  symbols are not respected '
    """
    temp = line.replace(r'\%','')
    cut = temp.find(r'%')
    if cut < 0:
        return temp.strip()
    else:
        return temp[0:cut].strip()


def removeInLineMath(line):
    """
    This function removes the inline math in the one line string 'line'
    """
    return re.sub( r'\$.*?\$', '', line ).strip()

def removeInLineCommands(line):
    """
    This function removes the LaTeX commands in the one line string 'line'.
    Should be called after removeInLineMath
    """
    return re.sub( r'\\\S+\{?.*?\}?', '', line ).strip()


def removeInlineMathAndCommands(line):
    """
    This function removes first the inline math and then the LaTeX commands in the
    one line string 'line'.
    """
    return removeInLineCommands( removeInLineMath( line ) )


def isEnvBegin(line):
    """
    This function returns True if the one line string 'line' is the
    opening of an environment. Otherwise False.
    """
    return line.lstrip().startswith(r'\begin')

def isEnvEnd(line):
    """
    This function returns True if the one line string 'line'
    is the closing of an environment. Otherwise False.
    """
    return line.lstrip().startswith(r'\end')

def skipEnv(handle):
    """
    This function takes as argument 'handle', which is a handle to the
    .tex source file and ignores all the lines inside an environment
    until the '\end' command is find. This function takes also into account
    the possibility of nested environments.
    """

    #depth of the environment recursion, if it is 0 whe are outside of all the nested environments
    recursion = 1

    while recursion > 0:
        line = handle.readline()
        if isEnvBegin(line):
            recursion +=1
        elif isEnvEnd(line):
            recursion -=1
    return


def skipPreamble(handle):
    """
    This function takes as argument 'handle', which is a handle to the
    .tex source file and ignores all the lines up to (including it) the
    line that has the '\begin{document}' command. The handle ends up
    pointing to the first line after '\begin{document}'
    """

    # If the handle is not at the start
    # of the file, move it there.
    if handle.tell(): handle.seek(0)

    while not next(handle).lstrip().startswith(r'\begin{document}'):
        pass
    return

# main method
def countAndMakeHistogram(fileName,nEntries=20):
    """
    arguments:

        fileName:   string with the filename

        nEntries:   integer representing the desired number of entries in the
                    histogram.
    """

    #Dictionary whose keys are the words, in lowercase, and whose
    #values are the number of times they are found in the text.
    words = dict()


    # handle to read the file
    f = open(fileName,'r')

    # Go to the first line after '\begin{document}'
    skipPreamble(f)
    print(next(f).rstrip())

    # Now, loop until we arrive to the '\end{document}'
    while not next(f).lstrip().startswith(r'\end{document}'):
        pass


    print(next(f).rstrip())

    return

if __name__=='__main__':


    # load the command line arguments
    fileName, nEntries = sys.argv[1:3]

    countAndMakeHistogram(fileName,nEntries)


    # words = []
    #
    # for line in f:
    #     #ignore the comments
    #     line = ignoreComments(line)
    #
    #     #ignore environments
    #     if isEnvBegin(line):
    #         skipEnv(f)
    #     else:
    #         #remove the equations and commands
    #         line = removeInlineMathAndCommands(line)
    #
    #         #add the words to the array words
    #         words.extend(line.split())
    #
    # f.close()
    # print(words)
