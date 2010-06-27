#!/usr/bin/env python

import sys, os
from os import path

base = path.abspath(path.join(path.dirname(__file__), path.pardir))
kvipy = path.join(base, 'kvipytools')

if kvipy in sys.path:
    sys.path.remove(kvipy)
sys.path.insert(0, kvipy)

os.chdir(base)

from kvipytools.run import main

main()

