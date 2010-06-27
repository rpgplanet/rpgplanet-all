#!/usr/bin/env python

from os import path
import sys
import os

try:
    from pip.req import parse_requirements
except ImportError:
    # fallback on earlier version of pip
    from pip import parse_requirements

class Options(object):
    '''dummy class because of bad options param handling in pip'''
    skip_requirements_regex = ''
    default_vcs = ''

def parse_req_url(url):
    vcs = None
    rev = None

    rest = url
    if '+' in url:
        vcs, rest = url.split('+')

    url, egg = rest.split('#')
    _, egg = egg.split('=')

    rev = None
    if '@' in url:
        url, rev = url.split('@')

    dir = url.strip('/').split('/')[-1]

    r = {
        'vcs': vcs,
        'url': url,
        'rev': rev,
        'egg': egg,
        'dir': dir,
    }
    return r

def _clone_all():
    thisdir = path.join(path.dirname(__file__), path.pardir)
    requirements_file = path.join(thisdir, 'requirements', 'thisenv.txt')
    requirements = list(parse_requirements(
        requirements_file, options=Options()))
    os.chdir(thisdir)
    for i in requirements:
        req = parse_req_url(i.url)
        req['dir'] = req['dir'].replace('.git', '')
        ref = get_reference(req['url'])
        if ref is not None:
            req['ref'] = ref
        if not path.exists(req['dir']):
            clone = 'git clone %(url)s' % req
            if req.has_key('ref'):
                clone = 'git clone --reference %(ref)s %(url)s' % req
            run_command(clone)
            os.chdir(req['dir'])
            run_command('git checkout -b %(rev)s origin/%(rev)s' % req)
            run_command('git checkout %(rev)s' % req)
            os.chdir('..')

def get_reference(url):
    '''
    find a reference dir for a repo

    TODO: move the logic somewhere else
    '''
    basedir = "C:/users/backup/100518/users/kvbik/GIT/source/githany"
    urlsplit = url.split('/')
    group = urlsplit[-3]
    repo = urlsplit[-1]
    dir = '%s/%s/%s' % (basedir, group, repo)
    if path.isdir(dir):
        return dir
    return None

def run_command(cmd):
    os.system(cmd)

def _main():
    if _test():
        _clone_all()
    sys.exit()

def _test():
    '''
    from nose.plugins.doctests import Doctest
    nose.runmodule('__main__', plugins=[Doctest(),])
    '''
    import doctest
    x = doctest.testmod()
    return not(x.failed)


if __name__ == '__main__':
    _main()

# vim: set et sw=4 ts=4:
