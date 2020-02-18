import re
import sys
from matplotlib import pyplot as plt

###################################################################
#        FUNCTIONS TO IGNORE PREAMBLES OF THE .TEX AND ENVIRONMENTS

# CHECK IF LINE IS THE START OF AN ENVIRONMENT
def isEnvBegin(line):
    """
    This function returns True if the one line string 'line' is the
    opening of an environment. Otherwise False.
    """
    return line.lstrip().startswith(r'\begin')

# CHECK IF LINE IS THE END OF AN ENVIRONMENT
def isEnvEnd(line):
    """
    This function returns True if the one line string 'line'
    is the closing of an environment. Otherwise False.
    """
    return line.lstrip().startswith(r'\end')

# SKIP THE ENVIRONMENTS
def skipEnv(handle):
    """
    This function takes as argument 'handle', which is a handle to the
    .tex source file and ignores all the lines inside an environment
    until the '\end' command is find. This function takes also into account
    the possibility of nested environments. At the end of this function the
    handle points to the first line after the environment end
    """

    # Depth of the environment recursion,
    # if it is 0 we are outside of all the
    # nested environments and the function
    # returns.
    recursion = 1

    while recursion > 0:
        line = handle.readline()
        if isEnvBegin(line):
            recursion +=1
        elif isEnvEnd(line):
            recursion -=1
    return handle.readline()

# GO TO THE START OF THE DOCUMENT
def goToStartDocument(handle):
    """
    This function takes as argument 'handle', which is a handle to the
    .tex source file and ignores all the lines up to (including it) the
    line that has the '\begin{document}' command. The handle ends up
    pointing to the first line after '\begin{document}'
    """

    # If the handle is not at the start
    # of the file, move it there.
    if handle.tell(): handle.seek(0)

    while not handle.readline().lstrip().startswith(r'\begin{document}'):
        pass
    return

###################################################################
#            FUNCTIONS TO PROCESS VALID LINES (outside environments)

# IGNORE COMMENTS
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

# REMOVE INLINE MATH
def removeInLineMath(line):
    """
    This function removes the inline math in the one line string 'line'
    """
    return re.sub( r'\$.*?\$', '', line ).strip()

# REMOVE INLINE COMMANDS
def removeInLineCommands(line):
    """
    This function removes the LaTeX commands in the one line string 'line'.
    Should be called after removeInLineMath
    """
    return re.sub( r'\\\S+\{?.*?\}?', '', line ).strip()

# REMOVE INLINE MATH AND COMMANDS
def removeInlineMathAndCommands(line):
    """
    This function removes first the inline math and then the LaTeX commands in the
    one line string 'line'.
    """
    return removeInLineCommands( removeInLineMath( line ) )

# RETURN THE WORDS IN THE LINE (in lower case)
def returnWords(line):
    """
    This function returns the words of a processed valid line as list
    of strings.
    """
    #extract the words
    words = re.findall( r'\b\w+\b' , line ) #words in the line

    #return the words in lowercase
    return list( map( lambda s: s.lower(), words ) )

# PROCEES THE LINE AND RETURN WORDS (in lower case)
def processAndReturnWords(line):
    """
    This function processes (ignore comments, remove math and commands)
    a valid (non environment) line and returns the words as list
    of strings.
    """
    #remove comments
    line = ignoreComments(line)

    #remove Inline math and commands
    line = removeInlineMathAndCommands(line)

    #return the words in lowercase
    return returnWords(line)


###############################################################################
#              FUNCTIONS TO COUNT WORD OCCURENCES

def updateWordsDict(words_array,words_dict):
    """
    This function update the dictionary "words_dict" with the words
    in the array "words_array".
    """

    for word in words_array:
        words_dict[word] = words_dict.get(word,0) + 1
    return


def analyzeTeXFile(file,words_dict,create_output_file = False):
    """
    This function takes as input "file", a path to a .tex file, and performs
    the word count. The "words_dict" dictionary is updated with the counts.
    "create_output_file" default value is False. If True, then the results of
    analyzing the .tex file are stored in a file named "file.txt" in the format
    word1: counts_word1
    word2: counts_word2
    .
    .
    The lines in the output file, are sorted by frequency (descending order) and
    alphabetically.
    """

    #Open file
    with open(file,'r') as f:
        # Go to the first line after '\begin{document}' and read it
        goToStartDocument(f)
        line = f.readline().rstrip()

        # dictionary containing the frequency of words in this text file
        words = dict()

        # Now, loop until we arrive to the '\end{document}'
        while not line.lstrip().startswith(r'\end{document}'):
            #skip environments
            if isEnvBegin(line):
                line = skipEnv(f)
                continue

            #process line and get the words
            line_words = processAndReturnWords(line)

            #Update the dictionary that contains the counts
            updateWordsDict(line_words,words)

            #go to following line
            line = f.readline()


    # Update the external dictionary
    for key in words:
        words_dict[key] = words_dict.get(key,0) + words[key]

    # Create file for the results if true
    if create_output_file:
        f_out_name = '{}__counts.txt'.format( re.findall(r'(\S+).tex',file)[0] )

        with open(f_out_name,'w') as f_out:
            for key in sorted(words, key = lambda k:(-words[k],k)):
                line = '{0}: {1}\n'.format(key,words[key])
                f_out.write(line)

    return

##############################################################################
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
    goToStartDocument(f)
    line = f.readline().rstrip()
    print(line)

    # Now, loop until we arrive to the '\end{document}'
    while not line.lstrip().startswith(r'\end{document}'):
        # PROCESSING THE LINES

        #skip environments
        if isEnvBegin(line):
            line = skipEnv(f)
            continue

        #process line and get the words
        line_words = processAndReturnWords(line)

        #Update the dictionary that contains the counts
        updateWordsDict(line_words,words)

        #go to following line
        line = f.readline()


    line = f.readline().rstrip()
    print(line)
    f.close()

    #file to store the words
    f = open('results.txt','w')
    word_count = 0
    for key in sorted(words, key = lambda k:(-words[k],k)):
        line = '{0}: {1}\n'.format(key,words[key])
        f.write(line)
        word_count += words[key]

    # print(word_count)
    f.close()

    sorted_counts = sorted(list(words.values()),reverse=True)
    # print(sorted_counts)
    fig, axes = plt.subplots()
    axes.scatter(range(len(sorted_counts)),sorted_counts)
    axes.set_xlim(0,25)
    fig.savefig('results.eps')

    return

if __name__=='__main__':


    # load the command line arguments
    fileName, nEntries = sys.argv[1:3]

    countAndMakeHistogram(fileName,nEntries)
