<div align="center">
  <img src="docs/img/logo_with_text.png" width="296" height="323">
  <br><br><br>
</div>


[![PyPi](https://img.shields.io/pypi/v/stockroom?style=for-the-badge)](https://pypi.python.org/pypi/stockroom)
[![lgtm](https://img.shields.io/lgtm/grade/python/github/tensorwerk/stockroom?style=for-the-badge)](https://lgtm.com/projects/g/tensorwerk/stockroom/)

A version control system for software 2.0.

# Introduction
Stockroom is a platform to version models, data, parameters, experiment artifacts etc. alongside git
versioned source code.

- It is **easy**. The APIs are very similar to dictionaries in python
- It **works alongside Git** - in case you need to version source code as well. It's OK if you don't.
- **High performance**, thanks to the amazing [hangar](https://github.com/tensorwerk/hangar-py) library
- [Upcoming] Tight **integration with PyTorch**. So that you don't need to write the complex pipeline code.  

# Why
One important motivation behind the initial design of stockroom is to avoid users
learning another tool for versioning. We try to make the APIs as minimal and familiar
as possible. Similar to other versioning tools, stockroom let "git" does ``checkout``
and rely on "git" to move between branches/commits. But unlike other tools, we channel
your data access through the smart API so that we don't need to move the huge data files
around when you traverse between commits.   



## Example
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


## Installation

```console
$ pip install stockroom
```

## License

This project is licensed under the terms of the **Apache Software License 2.0**
