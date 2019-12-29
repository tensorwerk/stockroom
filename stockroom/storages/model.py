import warnings

import numpy as np

from .. import parser
from ..repository import StockRepository
from ..utils import LazyLoader

torch = LazyLoader('torch', globals(), 'torch')
tf = LazyLoader('tf', globals(), 'tensorflow')


class ModelStore:
    """
    ModelStore class utilizes hangar arraysets to store the pieces of a model and
    use hangar metadata to store the information required to collate it back to
    a model. It right now supports ``keras.Model`` and ``torch.nn.Module`` models.
    ModelStore instance, on :meth:`storages.ModelStore.save` creates few arraysets
    (one arrayset for each data type) to store the weights and create one arrayset
    specifically to store the shape of each layer. This shape arrayset is needed
    because the weights of each layer would be flattened before saving. This is
    essential since handling variable shapes and variable ranks are more complex
    than flattening and reshaping-back the weights.
    """

    def __init__(self, write):
        self.co = None
        self._write = write
        self._repo = StockRepository()

    def save(self, name, model):
        if not self._write:
            raise PermissionError("ModelStore instance is not write-enabled")
        if hasattr(model, 'state_dict'):
            state = model.state_dict()
            weights = [x.numpy() for x in state.values()]
            layers = state.keys()
            library = 'torch'
            library_version = torch.__version__
        elif hasattr(model, 'get_weights'):
            library = 'tf'
            layers = None
            weights = model.get_weights()
            library_version = tf.__version__
        else:
            raise TypeError("Unknown model type. StockRoom can work with only "
                            "``Keras.Model`` or ``torch.nn.Module`` modules")
        longest = max([len(x.reshape(-1)) for x in weights])
        dtypes = [w.dtype.name for w in weights]

        co = self._repo.checkout(write=True)
        co.metadata[parser.model_metakey(name, 'library')] = library
        co.metadata[parser.model_metakey(name, 'libraryVersion')] = library_version
        co.metadata[parser.model_metakey(name, 'longest')] = str(longest)
        co.metadata[parser.model_metakey(name, 'dtypes')] = parser.stringify(dtypes)
        co.metadata[parser.model_metakey(name, 'numLayers')] = str(len(weights))
        co.metadata[parser.model_metakey(name, 'layers')] = parser.stringify(layers)

        # ---------- Create arraysets if not exist -----------------

        shapeKey = parser.shapekey(name, str(longest))
        if shapeKey not in co.arraysets.keys():
            co.arraysets.init_arrayset(shapeKey, 10, np.int64, variable_shape=True)
        for i, w in enumerate(weights):
            modelKey = parser.modelkey(name, str(longest), dtypes[i])
            if modelKey not in co.arraysets.keys():
                co.arraysets.init_arrayset(
                    modelKey, longest,np.dtype(dtypes[i]), variable_shape=True)

        # ---------------------------------------------------------

        with co:
            shape_aset = co.arraysets[shapeKey]
            for i, w in enumerate(weights):
                model_aset = co.arraysets[parser.modelkey(name, longest, dtypes[i])]
                model_aset[i] = w.reshape(-1)
                if w.shape:
                    shape_aset[i] = np.array(w.shape)
                else:
                    shape_aset[i] = np.array(()).astype('int64')
        co.close()

    def load(self, name, model):
        co = self._repo.checkout()

        try:
            library = co.metadata[parser.model_metakey(name, 'library')]
        except KeyError:
            raise KeyError(f"Model with key {name} not found")
        library_version = co.metadata[parser.model_metakey(name, 'libraryVersion')]
        longest = int(co.metadata[parser.model_metakey(name, 'longest')])
        dtypes = parser.destringify(co.metadata[parser.model_metakey(name, 'dtypes')])
        num_layers = int(co.metadata[parser.model_metakey(name, 'numLayers')])
        layers = parser.destringify(co.metadata[parser.model_metakey(name, 'layers')])

        shapeKey = parser.shapekey(name, longest)
        shape_aset = co.arraysets[shapeKey]
        weights = []
        for i in range(num_layers):
            modelKey = parser.modelkey(name, longest, dtypes[i])
            aset = co.arraysets[modelKey]
            w = aset[i].reshape(np.array(shape_aset[i]))
            weights.append(w)
        if library == 'torch':
            if torch.__version__ != library_version:
                warnings.warn(f"PyTorch version used while storing the model "
                              f"({library_version}) is not same as the one installed "
                              f"in the current environment. i.e {torch.__version__}")
            state = {layers[i]: torch.from_numpy(weights[i]) for i in range(num_layers)}
            model.load_state_dict(state)
        else:
            if tf.__version__ != library_version:
                warnings.warn(f"Tensorflow version used while storing the model "
                              f"({library_version}) is not same as the one installed "
                              f"in the current environment. i.e {tf.__version__}")
            model.set_weights(weights)


def modelstore(write=False):
    return ModelStore(write=write)
