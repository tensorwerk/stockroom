import numpy as np

from .storagebase import StorageBase
from ..utils import get_current_head, get_stock_root
from .. import parser


def get_aset(co, name, dtype=None, longest=None, variable=False):
    try:
        aset = co.arraysets[name]
        return aset
    except KeyError:
        pass
    aset = co.arraysets.init_arrayset(
        name, dtype=np.dtype(dtype), shape=(longest,), variable_shape=variable)
    return aset

# TODO: figure out what' the importance of max shape if var_shape is True


class ModelStore(StorageBase):
    def __init__(self):
        super().__init__()

    def save(self, name, model):
        # TODO: optimize
        co = self.repo.checkout(write=True)
        if hasattr(model, 'state_dict'):
            library = 'torch'
            state = model.state_dict()
            layers = list(state.keys())
            # TODO: forloop for all needs or list comprehension few times
            weights = [x.numpy() for x in state.values()]
            str_layer = parser.layers_to_string(layers)
            co.metadata[parser.metakey(name, 'layers')] = str_layer
        elif hasattr(model, 'get_weights'):
            library = 'tf'
            # tf model
            weights = model.get_weights()
        else:
            raise TypeError("Unknown model type. StockRoom can work with only "
                            "``Keras.Model`` or ``torch.nn.Module`` modules")
        longest = max([len(x.reshape(-1)) for x in weights])
        co.metadata[parser.metakey(name, 'library')] = library
        co.metadata[parser.metakey(name, 'longest')] = str(longest)
        co.metadata[parser.metakey(name, 'num_layers')] = str(len(weights))
        dtypes = [w.dtype.name for w in weights]
        str_dtypes = parser.dtypes_to_string(dtypes)
        co.metadata[parser.metakey(name, 'dtypes')] = str_dtypes
        aset_prefix = parser.model_asetkey_from_details(name, str(longest))
        co.metadata[parser.metakey(name, 'aset_prefix')] = aset_prefix
        shape_asetn = parser.shape_asetkey_from_model_asetkey(name)
        shape_aset = co.arraysets.init_arrayset(
            shape_asetn, shape=(10,), dtype=np.int64, variable_shape=True)
        for i, w in enumerate(weights):
            asetn = parser.model_asetkey_from_details(aset_prefix, dtypes[i])
            aset = get_aset(co, asetn, dtypes[i], longest, variable=True)
            aset[i] = w.reshape(-1)
            if w.shape:
                shape_aset[i] = np.array(w.shape)
            else:
                shape_aset[i] = np.array(()).astype('int64')
        co.close()

    def load(self, name, model):
        import torch
        root = get_stock_root()
        head_commit = get_current_head(root)
        co = self.repo.checkout(commit=head_commit)
        aset_prefix = co.metadata[parser.metakey(name, 'aset_prefix')]
        dtypes = parser.string_to_dtypes(co.metadata[parser.metakey(name, 'dtypes')])
        library = co.metadata[parser.metakey(name, 'library')]
        num_layers = int(co.metadata[parser.metakey(name, 'num_layers')])
        weights = []
        for i in range(num_layers):
            asetn = parser.model_asetkey_from_details(aset_prefix, dtypes[i])
            aset = get_aset(co, asetn)
            shape_asetn = parser.shape_asetkey_from_model_asetkey(name)
            shape_aset = co.arraysets[shape_asetn]
            w = aset[i].reshape(np.array(shape_aset[i]))
            weights.append(w)
        if len(weights) != num_layers:
            raise RuntimeError("Critical: length doesn't match. Raise an issue")
        if library == 'torch':
            str_layers = co.metadata[parser.metakey(name, 'layers')]
            layers = parser.string_to_layers(str_layers)
            if len(layers) != num_layers:
                raise RuntimeError("Critical: length doesn't match. Raise an issue")
            state = {layers[i]: torch.from_numpy(weights[i]) for i in range(num_layers)}
            model.load_state_dict(state)
        else:
            model.set_weights(weights)





