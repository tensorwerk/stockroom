=========
stockroom
=========


.. image:: https://img.shields.io/pypi/v/stockroom.svg
        :target: https://pypi.python.org/pypi/stockroom

.. image:: https://img.shields.io/travis/hhsecond/stockroom.svg
        :target: https://travis-ci.org/hhsecond/stockroom

.. image:: https://readthedocs.org/projects/stockroom/badge/?version=latest
        :target: https://stockroom.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




A hangar wrapper that enables the versioning of model, params and metrics along
with data


* Free software: Apache Software License 2.0
* Documentation: https://stockroom.readthedocs.io.

Introduction
------------
A platform to version models, data, parameters, metrics etc alongside git
versioned source code.
Stockroom exists for three reasons
- Work hand-in-hand with git
The git is probably the most prominent version controlling tool available in the market
that is being prevalent in the developers community. The advantage we get by making
stockroom work alongside git is that there is no new things to learn about versioning
your data.
- Simplify `hangar <https://github.com/tensorwerk/hangar-py>`_ APIs
Hangar is a really big tool that tries to serve all the need of data storage and
versioning in the deep learning/machine learning space without compromising the speed.
Essentially trying to do what git did for source code but for data. For achieving this,
along with the flexibility, hangar introduces a bunch of APIs. But by making it work
alongside git had a good side effect in simplifying these APIs.
- Make storage of model + data + params and versioning them possible in`hangar
<https://github.com/tensorwerk/hangar-py>`_

Even though stockroom is built on top of hangar, user doesn't need to understand hangar
to work with stockroom. Stockroom works like a normal python dictionary where user can
store data to and retrieve data from. Stockroom is currently in it's first ever release.
It doesn't have an exhaustive test suite and the APIs could change in backward
incompatible way (for good).

Example
=======
.. code-block:: python

    from stockroom import StockRoom
    import numpy as np

    stock = StockRoom()
    stock.data['sample1'] = np.random.random((3, 28, 28))

Checkout the `documentation <https://stockroom.readthedocs.io/en/latest/>`_ to learn more
