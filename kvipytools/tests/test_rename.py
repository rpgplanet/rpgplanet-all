
import os
from os.path import join
from shutil import rmtree
from unittest import TestCase
from tempfile import mkdtemp

from kvipytools.rename import (
    OptionParser, rename_files_dirs, change_content
)


class TestParse(TestCase):
    def setUp(self):
        self.option_parser = OptionParser()

    def test_option_parser(self):
        parsed = self.option_parser(['x=y', 'a a a=b b b'])
        expected = [('x', 'y'), ('a a a', 'b b b')]
        self.failUnlessEqual(expected, parsed)

    def test_options_with_equalsign_in_patterns(self):
        parsed = self.option_parser([r'x\=x\==y\=y\=', r'a a a\==\=b b b'])
        expected = [('x=x=', 'y=y='), ('a a a=', '=b b b')]
        self.failUnlessEqual(expected, parsed)

    def test_escaping_of_escape_char(self):
        parsed = self.option_parser([r'x\\=\\y'])
        expected = [('x\\', '\\y')]
        self.failUnlessEqual(expected, parsed)

    def test_split_string(self):
        split = self.option_parser.split_string('x=y')
        expected = ['x', '=', 'y']
        self.failUnlessEqual(expected, split)

    def test_replace_escaping_split_char(self):
        escaped = self.option_parser.escape_split(['\\', '=', '\\', '=', '='])
        expected = [-2, -2, '=']
        self.failUnlessEqual(expected, escaped)

    def test_replace_escaping_of_escape_char(self):
        escaped = self.option_parser.escape_escape(['\\', '\\', '\\', '\\', '\\'])
        expected = [-1, -1, '\\']
        self.failUnlessEqual(expected, escaped)

    def test_replace_escaping_if_escape_char_is_on_odd_places(self):
        escaped = self.option_parser.escape_escape(['a', '\\', '\\', 'b'])
        expected = ['a', -1, 'b']
        self.failUnlessEqual(expected, escaped)

    def test_split_list_via_equal_sign(self):
        values = [1, 2, 3, '=', 4, 5, 6]
        split = self.option_parser.split_via_equalsign(values)
        expected = ([1, 2, 3], [4, 5, 6])
        self.failUnlessEqual(expected, split)

    def test_list_replace_all(self):
        values = [1, 2, 3, 1, 2, 3]
        self.option_parser.list_replace_all(values, 1, 'one')
        self.option_parser.list_replace_all(values, 2, 'two')
        self.option_parser.list_replace_all(values, 3, 'three')
        expected = ['one', 'two', 'three', 'one', 'two', 'three']
        self.failUnlessEqual(expected, values)


class TestWithTmpDirCase(TestCase):
    TEST_DIR_STRUCTURE = (
        (join('.'), None),
        (join('.', 'x'), None),
        (join('.', 'x', 'a a a'), 'x\na a a'),
        (join('.', 'a a a'), None),
        (join('.', 'a a a', 'x'), 'a a a\nx'),
    )

    def setUp(self):
        self.options = (('x', 'y'), ('a a a', 'b b b'))

        self.oldcwd = os.getcwd()
        self.directory = mkdtemp(prefix='test_rename_tmp_dir_case_')
        os.chdir(self.directory)

        self.create_structure_from_variable(self.TEST_DIR_STRUCTURE)

    def create_structure_from_variable(self, dir_structure):
        '''
        create directory structure via given list of tuples (filename, content,)
        content being None means it is directory
        '''
        for filename, content in dir_structure:
            if content is None:
                try:
                    os.makedirs(filename)
                except OSError:
                    pass
            else:
                f = open(filename, 'w')
                f.write(content)
                f.close()

    def store_directory_structure(self, path):
        '''
        recursivelly traverse directory and store it in format
        that can be given to create_structure_from_variable()
        '''
        d = {}
        for base, dirs, files in os.walk(path):
            d[base] = None
            for i in files:
                fn = join(base, i)
                f = open(fn, 'r')
                d[fn] = f.read()
                f.close()
        return d.items()

    def tearDown(self):
        os.chdir(self.oldcwd)
        rmtree(self.directory)


class TestRenameFiles(TestWithTmpDirCase):
    def test_correct_filenames(self):
        rename_files_dirs(self.options)

        actual_structure = sorted(self.store_directory_structure('.'))
        expected_structure = sorted((
            (join('.'), None),
            (join('.', 'y'), None),
            (join('.', 'y', 'b b b'), 'x\na a a'),
            (join('.', 'b b b'), None),
            (join('.', 'b b b', 'y'), 'a a a\nx'),
        ))

        self.failUnlessEqual(expected_structure, actual_structure)


class TestChangeContent(TestWithTmpDirCase):
    def test_content_renamed(self):
        change_content(self.options)

        actual_structure = sorted(self.store_directory_structure('.'))
        expected_structure = sorted((
            (join('.'), None),
            (join('.', 'x'), None),
            (join('.', 'x', 'a a a'), 'y\nb b b'),
            (join('.', 'a a a'), None),
            (join('.', 'a a a', 'x'), 'b b b\ny'),
        ))

        self.failUnlessEqual(expected_structure, actual_structure)

