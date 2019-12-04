# TODO: best practices like utf8
# TODO: is this separater enough - add test cases?
SEP = '--_'
PREFIX = '_STOCK'


# ===================================================
#         Metadata & Arrayset key parsers
# ===================================================
def metakey(name, model):
    return f"{PREFIX}{SEP}{model}{SEP}{name}"


def modelkey(name, longest, dtype):
    return f"{PREFIX}{SEP}{name}{SEP}{longest}{SEP}{dtype}"


def shapekey(name, longest):
    return f"{PREFIX}{SEP}{name}{SEP}{longest}{SEP}{'shape'}"


# ====================================================
#         Metadata Value parsers
# ====================================================

# TODO: better names
def encode(layers):
    return ','.join(layers)


def decode(string):
    return string.split(',')
