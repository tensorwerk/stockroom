# TODO: best practices like utf8
# TODO: is this separater enough
SEP = '--_'
PREFIX = '_STOCK'


def metakey(model, name):
    return f"{PREFIX}_metakey_{model}_{name}"


def model_asetkey_from_details(*args):
    # TODO: make more reliable hash rather than time.time()
    asetkey = f"{PREFIX}{SEP}"
    return asetkey + SEP.join(args)


def shape_asetkey_from_model_asetkey(model_asetkey):
    return model_asetkey + '_shape'


# TODO: move this somewhere more sensib
def layers_to_string(layers):
    return ','.join(layers)


def string_to_layers(string):
    return string.split(',')


def dtypes_to_string(dtypes):
    return ','.join(dtypes)


def string_to_dtypes(string):
    return string.split(',')
