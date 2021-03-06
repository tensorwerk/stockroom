SEP = "--_"
PREFIX = "_STK"

# TODO: Move the parsing logic to each storage module


# ===================================================================
#         Metadata & Column key parsers for model store
# ===================================================================
def model_metakey(name):
    return f"{PREFIX}M{SEP}{name}{SEP}meta"


def modelkey(name, longest, dtype):
    return f"{PREFIX}M{SEP}{name}{SEP}{longest}{SEP}{dtype}"


def model_shapekey(name, longest):
    return f"{PREFIX}M{SEP}{name}{SEP}{longest}{SEP}shape"


# ===================================================================
#                      Metadata Value parsers
# ===================================================================


def stringify(lst):
    return ",".join(lst) if lst else ""


def destringify(string):
    return string.split(",") if string else ""


# ===================================================================
#                            Tag keys
# ===================================================================


def tagkey():
    return f"{PREFIX}{SEP}tag"


def tag_typekey():
    return f"{PREFIX}{SEP}tag{SEP}type"
