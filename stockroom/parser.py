SEP = '--_'
PREFIX = '_STK'


# ===================================================================
#         Metadata & Arrayset key parsers for model store
# ===================================================================
def model_metakey(model, name):
    return f"{PREFIX}{SEP}{model}{SEP}{name}"


def modelkey(name, longest, dtype):
    return f"{PREFIX}{SEP}{name}{SEP}{longest}{SEP}{dtype}"


def model_shapekey(name, longest):
    return f"{PREFIX}{SEP}{name}{SEP}{longest}{SEP}shape"


# ===================================================================
#                      Metadata Value parsers
# ===================================================================

def stringify(lst):
    return ','.join(lst) if lst else ''


def destringify(string):
    return string.split(',') if string else ''


# ===================================================================
#                            Tag keys
# ===================================================================

def tagkey(name):
    return f"{PREFIX}{SEP}tag{SEP}{name}"


def tag_typekey(name):
    return f"{PREFIX}{SEP}{name}{SEP}tag{SEP}type"
