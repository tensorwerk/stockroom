import warnings

import numpy as np

from .. import parser
from ..utils import LazyLoader

torch = LazyLoader('torch', globals(), 'torch')
tf = LazyLoader('tf', globals(), 'tensorflow')


class Model:
    """
    Model class utilizes hangar columns to store pieces of a model and use hangar
    metadata to store the information required to collate it back to a model. Currently,
    it supports ``keras.Model`` and ``torch.nn.Module`` models. ModelStore instance,
    on :meth:`stockroom.storages.Model.save_weights` creates few columns (one column for
    each data type) to store the weights and create one column specifically to store the
    shape of each layer. This shape column is needed because the weights of each layer
    would be flattened before saving. This is essential since handling variable shapes
    and variable ranks are more complex than flattening and reshaping-back the weights.

    Examples
    --------
    >>> import torch
    >>> import tensorflow as tf
    >>> torch_model = torch.Sequential(...)
    >>> stock.model['torch_model'] = torch_model.state_dict()
    >>> tf_model = tf.Keras.Sequential()
    >>> tf_model.add(tf.layers.Dense(64, activation='relu'))
    >>> stock.model['tf_model'] = tf_model.get_weights()

    But if you can make it easy by calling special functions that knows how to fetch
    weights from the model or how to put weights back to model. Checkout :meth:`Model.save_weights`
    & :meth:`Model.load_weights` for more details
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

        with self._repo.write_checkout() as co:
            co.metadata[parser.model_metakey(name, 'library')] = library
            co.metadata[parser.model_metakey(name, 'libraryVersion')] = library_version
            co.metadata[parser.model_metakey(name, 'longest')] = str(longest)
            co.metadata[parser.model_metakey(name, 'dtypes')] = parser.stringify(dtypes)
            co.metadata[parser.model_metakey(name, 'numLayers')] = str(len(weights))
            co.metadata[parser.model_metakey(name, 'layers')] = parser.stringify(layers)

            # ---------- Create arraysets if not exist -----------------
            shapeKey = parser.model_shapekey(name, str(longest))
            if shapeKey not in co.arraysets.keys():
                shape_typ = np.array(1).dtype  # C long = int32 in win64; int64 elsewhere
                co.arraysets.init_arrayset(shapeKey, 10, shape_typ, variable_shape=True)
            for i, w in enumerate(weights):
                modelKey = parser.modelkey(name, str(longest), dtypes[i])
                if modelKey not in co.arraysets.keys():
                    co.arraysets.init_arrayset(
                        modelKey, longest, np.dtype(dtypes[i]), variable_shape=True)
            # ---------------------------------------------------------

            shape_aset = co.arraysets[shapeKey]
            for i, w in enumerate(weights):
                model_aset = co.arraysets[parser.modelkey(name, longest, dtypes[i])]
                model_aset[i] = w.reshape(-1)
                if w.shape:
                    shape_aset[i] = np.array(w.shape)
                else:
                    # C long = int32 in win64; int64 elsewhere
                    shape_typ = np.array(1).dtype
                    shape_aset[i] = np.array(()).astype(shape_typ)

    def __getitem__(self, name):
        with self._repo.read_checkout() as co:
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
        A convenient function to call when you don't want to deal with weight extraction
        from the model, regardless of which framework do you use to write model, as far
        as that framework is supported by stockroom. This function expects the model
        object from one of the supported framework. This will call the corresponding
        function of that framework to fetch the weights and then call :meth:`Model.__setitem__`
        to save the weights.

        Parameters
        ----------
        name : str
            Name of the key to which the model parameters are saved
        model : Any
            Object from any supported framework

        Examples
        --------
        >>> stock.model.save_weights('torch_model', torch_model)

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
        for all the columns that matches the model name and reshape it back to the actual
        shape (actual shape is stored in another column). Different frameworks has
        different way of loading the parameter to model object. For identifying this,
        :meth:`Model.save_weights` also saves the framework name while saving the model

        Parameters
        ----------
        name :  str
            Name of the key from which the model parameters are loaded
        model :  Any
            Model object from any supported framework onto which the parameters are
            loaded. Loading the parameters is an inplace operation and hence this
            function doesn't return anything

        Examples
        --------
        >>> stock.model.load_weights('torch_model', torch_model)
        """
        weights = self[name]
        if hasattr(model, 'load_state_dict'):
            model.load_state_dict(weights)
        elif hasattr(model, 'set_weights'):
            model.set_weights(weights)
        else:
            raise TypeError("Unknown model type. StockRoom can work with only "
                            "``Keras.Model`` or ``torch.nn.Module`` modules")
