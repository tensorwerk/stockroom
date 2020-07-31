import warnings

import numpy as np

from stockroom import parser
from stockroom.utils import LazyLoader

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
    def __init__(self, accessor):
        self.accessor = accessor

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
        writer = self.accessor
        metakey = parser.model_metakey(name)
        if metakey not in writer.columns.keys():
            metacol = writer.add_str_column(metakey)
        else:
            metacol = writer[metakey]
        metacol['library'] = library
        metacol['libraryVersion'] = library_version
        metacol['longest'] = str(longest)
        metacol['dtypes'] = parser.stringify(dtypes)
        metacol['numLayers'] = str(len(weights))
        metacol['layers'] = parser.stringify(layers)

        # ---------- Create ndarray columns if doesn't exist -----------------
        shapeKey = parser.model_shapekey(name, str(longest))
        if shapeKey not in writer.columns.keys():
            shape_typ = np.array(1).dtype  # C long = int32 in win64; int64 elsewhere
            writer.add_ndarray_column(shapeKey, 10, shape_typ, variable_shape=True)
        for i, w in enumerate(weights):
            modelKey = parser.modelkey(name, str(longest), dtypes[i])
            if modelKey not in writer.columns.keys():
                writer.add_ndarray_column(
                    modelKey, longest, np.dtype(dtypes[i]), variable_shape=True)
        # ---------------------------------------------------------

        shape_col = writer.columns[shapeKey]
        for i, w in enumerate(weights):
            model_col = writer.columns[parser.modelkey(name, longest, dtypes[i])]
            model_col[i] = w.reshape(-1)

            if w.shape:
                shape_col[i] = np.array(w.shape)
            else:
                # C long = int32 in win64; int64 elsewhere
                shape_typ = np.array(1).dtype
                shape_col[i] = np.array(()).astype(shape_typ)

    def __getitem__(self, name):
        reader = self.accessor
        try:
            metakey = parser.model_metakey(name)
            metacol = reader.columns[metakey]
        except KeyError:
            raise KeyError(f"Model with key {name} not found")
        library = metacol['library']
        library_version = metacol['libraryVersion']
        longest = int(metacol['longest'])
        dtypes = parser.destringify(metacol['dtypes'])
        num_layers = int(metacol['numLayers'])
        layers = parser.destringify(metacol['layers'])

        shapeKey = parser.model_shapekey(name, longest)
        shape_col = reader.columns[shapeKey]
        weights = []
        for i in range(num_layers):
            modelKey = parser.modelkey(name, longest, dtypes[i])
            col = reader.columns[modelKey]
            w = col[i].reshape(np.array(shape_col[i]))
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
