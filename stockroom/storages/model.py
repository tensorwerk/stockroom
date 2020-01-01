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
        self._write = write
        self._repo = StockRepository()

    def save(self, name, model):
        """
        Saves the model to hangar repository. This function gets the ``torch.nn``
        or ``keras.Model`` object on which the corresponding function will be
        called to fetch the parameters. All the weights are then flattened to a one
        dimensional array. This is for avoiding the complexity of managing different
        shaped parameter tensors. However, we still need to make different arraysets
        for different data types.

        :param name: str, Name of the key to which the model parameters are saved
        :param model: Model object. ``torch.nn`` or ``keras.Model`` object
        """
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
        try:
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
        finally:
            co.close()

    def load(self, name, model):
        """
        Load the parameters from hangar repo, put it back to the model object. It looks
        for all the arraysets that matches the model name and reshape it back to the
        actual shape (actual shape is stored in another arrayset). Different frameworks
        has different way of loading the parameter to model object. For identifying
        this, ``save`` method also saves the framework name while saving the model

        :param name:  str, Name of the key to which the model parameters are saved
        :param model:  Model object. ``torch.nn`` or ``keras.Model`` object onto which
            the parameters are loaded. Loading the parameters is an inplace operation
            and hence this function doesn't return anything
        """
        co = self._repo.checkout(write=self._write)

        try:
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
        finally:
            co.close()


def modelstore(write=False):
    return ModelStore(write=write)
