
import sys, os
from os import path
from shutil import rmtree
from unittest import TestCase
from tempfile import mkdtemp

from kvipytools.run import (
    CMD, C, D,
    parse_options,
    import_config_file,
    eval_option, eval_dirs, eval_command,
    run, main,
)


RUNCOMMAND = '''\
DIRS = (
    '/tmp/abraka',
    '/tmp/brekeke',
)
command = 'pwd'
'''


def give_mocked_run_command(output):
    def run_command(cmd, quiet):
        output.append((os.getcwd(), cmd,))
    return run_command

class TestRunCase(TestCase):
    def setUp(self):
        # store curr path
        self.oldcwd = os.getcwd()

        # create test dir structure
        self.directory = mkdtemp(prefix='test_run_testrun_')

        # make some subdirs
        os.chdir(self.directory)
        for d in ('a', 'b', 'c'):
            os.makedirs(d)

        # create runcommand file
        self.configname = 'runcommand'
        self.configfile = '%s.py' % self.configname
        self.runfile = path.join(self.directory, self.configfile)
        f = open(self.runfile, 'w')
        f.write(RUNCOMMAND)
        f.close()

    def tearDown(self):
        # go back
        os.chdir(self.oldcwd)

        # dir cleanup
        rmtree(self.directory)

        # clear imported module
        if sys.modules.has_key(self.configname):
            del sys.modules[self.configname]

class TestRunInternals(TestRunCase):
    def test_import_config_file(self):
        m = import_config_file(self.configfile)

        self.failUnlessEqual(type(os), type(m))
        self.failUnlessEqual(self.configname, m.__name__)
        self.failUnlessEqual(path.join(self.directory, self.configfile), m.__file__)

    def test_import_config_file_sys_path_is_same_on_the_end(self):
        oldpath = sys.path[:]
        m = import_config_file(self.configfile)
        newpath = sys.path[:]

        self.failUnlessEqual(oldpath, newpath)

    def test_import_config_file_contains_correct_values(self):
        m = import_config_file(self.configfile)

        DIRS = (
            '/tmp/abraka',
            '/tmp/brekeke',
        )
        command = 'pwd'

        self.failUnlessEqual(DIRS, getattr(m, 'DIRS'))
        self.failUnlessEqual(command, getattr(m, 'command'))

    def test_eval_option(self):
        class Config(object):
            pass

        config = Config()
        option = 'a'
        value  = 'A'

        setattr(config, option, value)

        o = eval_option(option, config)

        self.failUnlessEqual(value, o)

    def test_eval_dirs(self):
        class Config(object):
            pass
        config = Config()

        config.A = ('a', 'b')
        config.B = ('e', 'f')

        dirs = eval_dirs(['_', 'A', 'c', 'd', 'B'], config)
        expected = ['a', 'b', 'c', 'd', 'e', 'f']

        self.failUnlessEqual(expected, dirs)

class TestRunWholeCommand(TestRunCase):
    def fail_unless_equal_main_with_this_argv(self, runfile='', argv=[], expected=[]):
        # catch output
        output = []
        run_command = give_mocked_run_command(output)

        # call main func without arguments
        main(runfile=runfile, argv=argv, run_command=run_command)

        self.failUnlessEqual(expected, output)

    def test_run_with_dummiest_values(self):
        d = self.directory
        argv = []
        expected = [
            (d, CMD),
            (d, CMD),
        ]
        self.fail_unless_equal_main_with_this_argv(argv=argv, expected=expected)

    def test_run_with_some_command(self):
        d = self.directory
        c = 'command'
        argv = [c]
        expected = [
            (d, CMD),
            (d, c),
        ]
        self.fail_unless_equal_main_with_this_argv(argv=argv, expected=expected)

    def test_run_with_some_command_and_dirs(self):
        d = self.directory
        c = 'command'
        argv = [c, 'a', 'b', 'c']
        expected = [
            (path.join(d, 'a'), CMD),
            (path.join(d, 'a'), c),
            (path.join(d, 'b'), CMD),
            (path.join(d, 'b'), c),
            (path.join(d, 'c'), CMD),
            (path.join(d, 'c'), c),
        ]
        self.fail_unless_equal_main_with_this_argv(argv=argv, expected=expected)

    def test_run_with_dir_variable(self):
        d = self.directory
        c = "command from command"
        argv = ['c', 'D']

        da = path.join(d, 'a')
        db = path.join(d, 'b')
        dc = path.join(d, 'c')

        runfilecontent = 'D = %s\nc = "%s"\n' % ((da, db, dc), c)
        f = open(self.runfile, 'w')
        f.write(runfilecontent)
        f.close()

        expected = [
            (da, CMD),
            (da, c),
            (db, CMD),
            (db, c),
            (dc, CMD),
            (dc, c),
        ]

        self.fail_unless_equal_main_with_this_argv(runfile=self.runfile, argv=argv, expected=expected)

    def test_with_real_run_command(self):
        cmd = '''"%s" -c "f = file('x', 'w'); f.write('xxx'); f.close();"''' % sys.executable
        argv = [cmd, 'a', 'b', 'c']

        main(argv=argv, quiet=True)

        self.failUnlessEqual(['x'], os.listdir('./a/'))
        self.failUnlessEqual(['x'], os.listdir('./b/'))
        self.failUnlessEqual(['x'], os.listdir('./c/'))

