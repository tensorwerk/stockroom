=========
Stockroom
=========


.. image:: https://img.shields.io/pypi/v/stockroom.svg
        :target: https://pypi.python.org/pypi/stockroom

.. image:: https://travis-ci.com/tensorwerk/stockroom.svg?branch=master
        :target: https://travis-ci.com/tensorwerk/stockroom

.. image:: https://readthedocs.org/projects/stockroom/badge/?version=latest
        :target: https://stockroom.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/codecov/c/github/tensorwerk/stockroom
        :target: https://codecov.io/gh/tensorwerk/stockroom/
        :alt: Codecov

.. image:: https://img.shields.io/lgtm/grade/python/github/tensorwerk/stockroom
        :target: https://lgtm.com/projects/g/tensorwerk/stockroom/
        :alt: LGTM Grade

Stockroom is a platform to version models, data, parameters, metrics etc. alongside git
versioned source code. It is licensed as a Free software under
**Apache Software License 2.0**

Introduction
------------
Stockroom is built on top of `hangar <https://github.com/tensorwerk/hangar-py>`_ and hence
is high performant but with a minimal and simple set of APIs. We tried to reduce the
cognitive overload as much as possible for a new user to get started. So stockroom is not
exactly a wrapper that blinds you from the internal hangar philosophy but it's a tool
that enables you to do things easy.

Stockroom is currently in it's first ever release. It doesn't have an exhaustive test
suite and the APIs could change in backward incompatible way (for good).

Why
---
Stockroom exists for three reasons

- Work hand-in-hand with git:

Stockroom let git does ``checkout`` and rely on that to move between branches/commits.
This allows stockroom to present a very simple and intuitive API collection to the user
while avoiding the need of user learning another set of commands otherwise they'd need.

- Simplify `hangar <https://github.com/tensorwerk/hangar-py>`_ APIs:

Hangar is an extensive and reliable tool that allows users to have fine grained control
for storing and versioning data without compromising the speed and efficiency.
Essentially trying to do what git did for source code but for data. But the set of APIs
hangar provides are also extensive and can be cut short if we can delegate few tasks to
git and make certain assumptions. And that's exactly what stockroom does

- Make storage of model + data + params + metrics and versioning them possible in `hangar <https://github.com/tensorwerk/hangar-py>`_



Example
=======
.. code-block:: python

    from stockroom import StockRoom
    import numpy as np

    stock = StockRoom()
    stock.data['sample1'] = np.random.random((3, 28, 28))

