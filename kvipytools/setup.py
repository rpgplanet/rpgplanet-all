from setuptools import setup
from os.path import join, dirname

base = dirname(__file__)

setup(
    name = 'KviPyTools',
    description = "kvbik's python tools",
    url = "http://github.com/kvbik/python-scripts",
    version = '0.1.0',
    author = "Jakub Vysoky",
    author_email = "jakub@borka.cz",
    license = "BSD",
    packages = ['kvipytools'],
    scripts = [join(base, 'scripts', 'rename.sh')], # TODO: this is not enough.. setup.py must be called from its dir: python setup.py argv
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'rename = kvipytools.rename:main',
            'run = kvipytools.run:main',
        ],
    }
)

