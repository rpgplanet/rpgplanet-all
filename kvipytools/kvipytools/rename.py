#!/usr/bin/env python

import sys, os

class OptionParser(object):
    '''
    parser commandline optiones separated by given separator::

      ./rename.py a=b c=d "a a a=b b b" a\\==\\=b

    will result into something like this::

      opts = [ ('a', 'b'), ('c', 'd'), ('a a a', 'b b b'), ('a=', '=b') ]
    '''
    def __init__(self, escape_char='\\', escape_replacement=-1, splitter_char='=', splitter_replacement=-2):
        self.escape_char = escape_char
        self.escape_replacement = escape_replacement
        self.splitter_char = splitter_char
        self.splitter_replacement = splitter_replacement

    def split_string(self, string):
        return [ c for c in string ]

    def replace_pair(self, chars, pair, replacement):
        '''
        go through chars in pairs and if two chars equals given pair
        put some special mark instead
        '''
        escaped_chars = []
        hop = False
        for i, j in enumerate(chars):
            if hop:
                hop = False
                continue
            if i < (len(chars) - 1):
                if (j, chars[i+1]) == pair:
                    hop = True
                    x = replacement
                else:
                    x = j
            else:
                x = j
            escaped_chars.append(x)
        return escaped_chars

    def escape_escape(self, chars):
        pair = (self.escape_char, self.escape_char)
        return self.replace_pair(chars, pair, self.escape_replacement)

    def escape_split(self, chars):
        pair = (self.escape_char, self.splitter_char)
        return self.replace_pair(chars, pair, self.splitter_replacement)

    def split_via_equalsign(self, chars, splitter='='):
        index = chars.index(splitter)
        return (chars[:index], chars[index+1:])

    def list_replace_all(self, seq, obj, repl):
        for i, elem in enumerate(seq):
            if elem == obj:
                seq[i] = repl

    def __call__(self, opts):
        """
        parse options given on cmdline separated by equal sign:
        >>> OptionParser()(['a=b', 'x x x=y y y'])
        [('a', 'b'), ('x x x', 'y y y')]
        """
        parsed_opts = []
        for o in opts:
            o = self.escape_escape(o)
            o = self.escape_split(o)
            l, r = self.split_via_equalsign(o)
            for i in l, r:
                self.list_replace_all(i, self.splitter_replacement, self.splitter_char)
                self.list_replace_all(i, self.escape_replacement, self.escape_char)
            parsed_opts.append((''.join(l), ''.join(r)))
        return parsed_opts

def call_command(cmd, options, verbose=False):
    """
    helper function that call shell command for every tuple in options
    """
    for patrn, repl in options:
        repl = {'patrn': patrn, 'repl': repl,}
        command = cmd % repl
        print 'running: %s' % command
        if not verbose:
            command += '&>/dev/null'
        os.system(command)

def rename_files_dirs(options):
    """
    rename all dirs and files to new name defined via options
    """
    # create dirs first
    call_command('''find . -type d | while read f; do mkdir -p "$(echo $f | sed 's/%(patrn)s/%(repl)s/g')"; done''', options)
    # than move files
    call_command('''find . -type f | while read f; do mv "$f"  "$(echo $f | sed 's/%(patrn)s/%(repl)s/g')"; done''', options)
    # delete empty dirs
    call_command('''find -depth -type d -empty -exec rmdir {} \;''', [(1,1)])

def change_content(options):
    """
    take file by file and replace any occurence of pattern with its replacement
    """
    call_command('''grep -r -l -- '%(patrn)s' . | tr '\\n' '\\0' | xargs -0 sed -i "s/%(patrn)s/%(repl)s/g"''', options)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parse_options = OptionParser()
    options = parse_options(sys.argv[1:])
    rename_files_dirs(options)
    change_content(options)


if __name__ == '__main__':
    main()

