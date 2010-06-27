
#META = (
#)

LIBS = (
    'rpghrac',
    'rpgplanet',
)

PROJS  = (
    'rpghrac',
    'rpgplanet',
)

UTILS = (
    'kvipytools',
)

PACKAGES = LIBS + PROJS
METAVERSION = PACKAGES + META
ALL = METAVERSION + UTILS

# defaults
_ALL = METAVERSION
_cmd = 'git status'

