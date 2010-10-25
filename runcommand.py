
META = (
     'rpgplanet-meta',
)

LIBS = (
    'esus',
)

PROJS  = (
    'rpghrac',
    'rpgplanet',
    'rpgcommon',
    'metaplayer',
    'rpgscheduler',
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

