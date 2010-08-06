
META = (
     'rpgplanet-meta',
)

LIBS = (
)

PROJS  = (
    'rpghrac',
    'rpgplanet',
    'rpgcommon',
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

