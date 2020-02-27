import re
import sys

"""
Convention: 'text' = string containing all text in file
            'content' = array containing the lines of file
            'line'
"""


# RETURN THE BODY OF THE DOCUMENT AND THROW AWAY EVERYTHING ELSE
def _returnDocumentBody(text):
    """
    This function takes as argument the string containing the text of
    the .tex source file and returns the string containing the text
    between '\begin{document}' and '\begin{document}'
    """
    match = re.search(r'\\begin{document}([\s\S]*?)\\end{document}', text)
    if match:
        return match.group(1).strip()
    return ''

# FUNCTIONS TO IGNORE THE CONTENT IN THE ENVIRONMENTS
def _which_environments(text):
    """
    Finds all the environments in 'text'. Returns a dictionary of
    strings (keys) corresponding to all the present environments.
    If the environment has been redefined, the value of the key
    is another dictionary containing the key: value pairs
        {'begin': 'new command for begin environment',
        'end': 'new command for end environment'}
    If the environment commands have not been redefined, its dictionary
    is empty.
    """
    env_list = re.findall(r'\\begin{(.+?)}', text)
    env_dict = dict()
    for env in env_list:
        env_dict[env] = {}

    #find if the environments have been redefined
    for env in env_dict:
        env_begin = re.findall(r'\\newcommand{(\S+)}{\\begin{' + env.replace('*','\\*') + r'}}',text)
        env_end   = re.findall(r'\\newcommand{(\S+)}{\\end{' + env.replace('*','\\*') + r'}}',text)
        if env_begin and env_end:
            env_dict[env]['begin'] = env_begin[0]
            env_dict[env]['end'] = env_end[0]
    return env_dict

def _remove_environment(text, env, redefined_env=None):
    """
    returns the text with all the  '\\begin{environment}*\\end{environment}'
    removed'.
    """
    text = re.sub(
        r'\\begin{' + env.replace('*','\\*') + r'}[\s\S]*?\\end{' + env.replace('*','\\*') + r'}',
        '', text)
    if redefined_env:
        begin = redefined_env['begin'].replace('\\','\\\\')
        end = redefined_env['end'].replace('\\','\\\\')
        text = re.sub(
            begin + r'[\s\S]*?' + end,
            '', text)
    return text

def _remove_all_environments(text,envs):
    for env in envs:
        text = _remove_environment(text,env,envs[env])
    return text

# REMOVE COMMENTS
def _remove_comments_inline(line):
    """Removes the comments from the string 'line'."""
    if 'auto-ignore' in line:
        return line
    if line.lstrip(' ').lstrip('\t').startswith('%'):
        return ''
    match = re.search(r'(?<!\\)%', line)
    if match:
        return line[:match.end()] + '\n'
    else:
        return line

def _remove_all_comments(content):
    """Erases all LaTeX comments in the content, and writes it."""
    content = [_remove_comments_inline(line) for line in content]
    return content

###############################################################################
#              FUNCTIONS TO COUNT WORD OCCURENCES

def _updateWordsDict(words_array,words_dict):
    """
    This function updates the dictionary "words_dict" with the words
    in the array "words_array".
    """
    for word in words_array:
        words_dict[word] = words_dict.get(word,0) + 1
    return


def analyzeTeXFile(file,words_external,create_output_file = False):
    """
    This function takes as input "file", a path to a .tex file, and performs
    the word count. The "words_external" dictionary is updated with the counts.
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
        #extract content
        content = f.readlines()
        #remove comments
        content = _remove_all_comments(content)
        #find environments
        envs = _which_environments(''.join(content))
        #get document body
        content = _returnDocumentBody(''.join(content))
        #get document without environments
        content = _remove_all_environments(content,envs).split('\n')
        #Extract the words and put them in lower case
        word_list = [ w.lower() for w in re.findall('[a-zA-Z]+','\n'.join(content)) ]
        #internal Dictionary
        words_internal = {}
        #Update the internal dictionary
        _updateWordsDict(word_list,words_internal)
        #Update the external dictionary
        _updateWordsDict(word_list,words_external)

        # Create file for the resuts if true
        if create_output_file:
            f_out_name = '{}__counts.txt'.format( re.findall(r'(\S+).tex',file)[0] )
            with open(f_out_name,'w') as f_out:
                for key in sorted(words_internal, key = lambda k:(-words_internal[k],k)):
                    line = '{0}: {1}\n'.format(key,words_internal[key])
                    f_out.write(line)
    return

##############################################################################
# main method


if __name__=='__main__':
    print('WIP')
