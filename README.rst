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
Althouh it is built as a high level API kit for `hangar
<https://github.com/tensorwerk/hangar-py>`_ and comes as part of hangar
itself, user doesn't need to know any founding philosophy of hangar work with
stockroom unless you need fine grained control. Stockroom is currently in it's
first ever release. It doesn't have an exhaustive test suite, although it should
work on any platform, we have tested it only on linux so far and the APIs could
change in backward incompatible way (for good). But the underlying idea of the
existence of stockroom is
- Ease the storage and versioning of data, model, hyper parameters and even metadata related to a specific run
- Make it work with git and hence avoid the steep learning curve but at the same time make sure you are not paying for the performance which you would if you are relying only on git for data storage
