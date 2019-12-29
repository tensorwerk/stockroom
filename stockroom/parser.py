SEP = '--_'
PREFIX = '_STOCK'


# ===================================================================
#         Metadata & Arrayset key parsers for model store
# ===================================================================
def model_metakey(model, name):
    return f"{PREFIX}{SEP}{model}{SEP}{name}"


def modelkey(name, longest, dtype):
    return f"{PREFIX}{SEP}{name}{SEP}{longest}{SEP}{dtype}"


def shapekey(name, longest):
    return f"{PREFIX}{SEP}{name}{SEP}{longest}{SEP}{'shape'}"


# ===================================================================
#                      Metadata Value parsers
# ===================================================================

def stringify(lst):
    return ','.join(lst) if lst else ''


def destringify(string):
    return string.split(',') if string else ''


# ===================================================================
#                             Params key
# ===================================================================


def params_metakey(name):
    return f"{PREFIX}{SEP}param{SEP}{name}"


# ===================================================================
#                            Generic key
# ===================================================================

def generic_metakey(name):
    return f"{PREFIX}{SEP}generic{SEP}{name}"
