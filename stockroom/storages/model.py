import warnings

import numpy as np

from .. import parser
from ..utils import LazyLoader

torch = LazyLoader('torch', globals(), 'torch')
tf = LazyLoader('tf', globals(), 'tensorflow')


class Model:
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

    def __init__(self, repo):
        self._repo = repo

    def __setitem__(self, name, weights):
        if isinstance(weights, dict):
            layers = weights.keys()
            weights = [x.numpy() for x in weights.values()]
            library = 'torch'
            library_version = torch.__version__
        elif isinstance(weights, list):
            library = 'tf'
            layers = None
            library_version = tf.__version__
        else:
            raise TypeError("Unknown type. Weights has to be a dict or list")
        longest = max([len(x.reshape(-1)) for x in weights])
        dtypes = [w.dtype.name for w in weights]

        with self._repo.checkout(write=True) as co:
            co.metadata[parser.model_metakey(name, 'library')] = library
            co.metadata[parser.model_metakey(name, 'libraryVersion')] = library_version
            co.metadata[parser.model_metakey(name, 'longest')] = str(longest)
            co.metadata[parser.model_metakey(name, 'dtypes')] = parser.stringify(dtypes)
            co.metadata[parser.model_metakey(name, 'numLayers')] = str(len(weights))
            co.metadata[parser.model_metakey(name, 'layers')] = parser.stringify(layers)

            # ---------- Create arraysets if not exist -----------------

            shapeKey = parser.model_shapekey(name, str(longest))
            if shapeKey not in co.arraysets.keys():
                co.arraysets.init_arrayset(shapeKey, 10, np.int64, variable_shape=True)
            for i, w in enumerate(weights):
                modelKey = parser.modelkey(name, str(longest), dtypes[i])
                if modelKey not in co.arraysets.keys():
                    co.arraysets.init_arrayset(
                        modelKey, longest, np.dtype(dtypes[i]), variable_shape=True)

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

    def __getitem__(self, name):
        # TODO: This will not read from stg
        with self._repo.checkout() as co:
            try:
                library = co.metadata[parser.model_metakey(name, 'library')]
            except KeyError:
                raise KeyError(f"Model with key {name} not found")
            library_version = co.metadata[parser.model_metakey(name, 'libraryVersion')]
            longest = int(co.metadata[parser.model_metakey(name, 'longest')])
            dtypes = parser.destringify(co.metadata[parser.model_metakey(name, 'dtypes')])
            num_layers = int(co.metadata[parser.model_metakey(name, 'numLayers')])
            layers = parser.destringify(co.metadata[parser.model_metakey(name, 'layers')])

            shapeKey = parser.model_shapekey(name, longest)
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
                return {layers[i]: torch.from_numpy(weights[i]) for i in range(num_layers)}

            else:
                if tf.__version__ != library_version:
                    warnings.warn(f"Tensorflow version used while storing the model "
                                  f"({library_version}) is not same as the one installed "
                                  f"in the current environment. i.e {tf.__version__}")
                return weights

    def save_weights(self, name, model):
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
        if hasattr(model, 'state_dict'):
            weights = model.state_dict()
        elif hasattr(model, 'get_weights'):
            weights = model.get_weights()
        else:
            raise TypeError("Unknown model type. StockRoom can work with only "
                            "``Keras.Model`` or ``torch.nn.Module`` modules")
        self[name] = weights

    def load_weights(self, name, model):
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
        weights = self[name]
        if hasattr(model, 'load_state_dict'):
            model.load_state_dict(weights)
        elif hasattr(model, 'set_weights'):
            model.set_weights(weights)
        else:
            raise TypeError("Unknown model type. StockRoom can work with only "
                            "``Keras.Model`` or ``torch.nn.Module`` modules")
