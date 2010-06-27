#!/usr/bin/env python

import sys, os
from os import path
from subprocess import Popen, PIPE


C = '_cmd'
D = '_ALL'

CMD = '"%s" -c "import os; print os.getcwd()"' % sys.executable


def parse_options(argv=[]):
    '''
    parse options from sys.argv
    '''
    if not len(argv):
        return (C, D)
    elif len(argv) == 1:
        return (argv[0], D)
    return argv

def import_config_file(runfile=''):
    '''
    import python file with some config values

    slightly inspired by: fabric.main:load_fabfile
    '''
    dir = os.getcwd()
    apath = path.join(dir, runfile)

    if not path.isfile(apath):
        return

    # get real path
    apath = path.abspath(apath)
    fpath = path.basename(apath)
    dpath = path.dirname(apath)
    # save old path
    oldpath = sys.path[:]
    # insert this dir to beginning of path
    sys.path.insert(0, dpath)
    # import it
    m = None
    if fpath[-3:] == '.py':
        m = __import__(fpath[:-3], {}, {}, [])
    # restore path
    sys.path = oldpath
    return m

def eval_option(option, config):
    '''
    evaluate one option from config file
    if it is not there, return what was given
    '''
    defaults = {
        C: CMD,
        D: os.getcwd(),
    }
    return getattr(config, option, defaults.get(option, option))

def eval_dirs(options, config):
    '''
    evaluate dir variables into actual directories
    or return the same dir name
    '''
    l = []
    for o in options[1:]:
        x = eval_option(o, config)
        if hasattr(x, '__iter__'):
            l.extend(x)
        else:
            l.append(x)
    return l

def eval_command(options, config):
    '''
    evaluate command variable or return the same
    '''
    return eval_option(options[0], config)

def run_command(cmd, quiet=False):
    shell = sys.platform != 'win32'
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=shell)
    stdoutdata, stderrdata = p.communicate()
    if not quiet:
        for o in stdoutdata.strip(), stderrdata.strip():
            # print both stdoutdata and stderrdata, but if it contains data only
            if o:
                print o
        if cmd != CMD:
            # if i am not the defautl path command, print one more empty line
            print

def run(command, dirs, run_command=run_command, quiet=False):
    '''
    run specified command in given directories
    '''
    base = os.getcwd()
    for d in dirs:
        os.chdir(d)
        run_command(CMD, quiet=quiet)
        run_command(command, quiet=quiet)
        os.chdir(base)

def main(runfile='runcommand.py', argv=None, run_command=run_command, quiet=False):
    if argv is None:
        argv = sys.argv[1:]

    options = parse_options(argv)
    config = import_config_file(runfile)

    dirs = eval_dirs(options, config)
    command = eval_command(options, config)

    run(command, dirs, run_command, quiet)


if __name__ == '__main__':
    main()

