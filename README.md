<div align="center">
  <img src="docs/en/docs/img/logo.png" width="296" height="323">
  <br><br><br>
</div>


[![PyPi](https://img.shields.io/pypi/v/stockroom?style=for-the-badge)](https://pypi.python.org/pypi/stockroom)
[![CodeCov](https://img.shields.io/codecov/c/github/tensorwerk/stockroom?style=for-the-badge)](https://codecov.io/gh/tensorwerk/stockroom/)
[![lgtm](https://img.shields.io/lgtm/grade/python/github/tensorwerk/stockroom?style=for-the-badge)](https://lgtm.com/projects/g/tensorwerk/stockroom/)

Stockroom is a platform to version models, data, parameters, metrics etc. alongside git
versioned source code. It is licensed as a Free software under
**Apache Software License 2.0**

# Introduction
Stockroom is built on top of [hangar](https://github.com/tensorwerk/hangar-py) & hence
is high performing. It abstracts away few hangar APIs by making assumptions and 
operating implicitly. One good example for such implicit decision-making is the
"checkout management". Stockroom, as a package, is not self-contained and whenever
possible, off load the heavy lifting to hangar's well written APIs. However,
the tutorials and documentations are self-contained to make sure users
doesn't have to run through different places to start working on stockroom.


# Why
One important motivation behind the initial design of stockroom is to avoid users
learning another tool for versioning. We try to make the APIs as minimal and familiar as
possible while relying on other popular tools such as git & hangar. Stockroom let "git"
does ``checkout`` and rely on "git" to move between branches/commits. This allows
stockroom to present a very simple and intuitive API collection to the user
while avoiding the need of user learning another set of commands otherwise they'd need.
In a nutshell, Stockroom exists for three reasons

- Work hand-in-hand with git
- Make it possible to version model, data, hyper-parameters metrics etc.
- Making versioning easy for [software 2.0](https://medium.com/@karpathy/software-2-0-a64152b37c35) stack



## Example
.. code-block:: python

    from stockroom import StockRoom
    import numpy as np

    stock = StockRoom()
    weights = stock.model['resnet50']
    model = make_model(weights)
    for e in range(epochs):
        for i in range(limit):
            x, y = stock.data['dataset', i]
            out = model(x)
            update_weights(out, y)
            if loss < previous_loss:
                stock.model['resnet50'] = get_weights(model)
                stock.commit('adding a better model)

