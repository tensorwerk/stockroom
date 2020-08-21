<div align="center">
  <img src="img/logo_with_text.png" width="296" height="323">
  <br><br><br>
</div>



<p align="center">
    <a href="https://codecov.io/gh/tensorwerk/stockroom"><img alt="Codecov" src="https://img.shields.io/codecov/c/github/tensorwerk/stockroom?style=for-the-badge"></a>
    <a href="https://pypi.python.org/pypi/stockroom"><img alt="pypi" src="https://img.shields.io/pypi/v/stockroom?style=for-the-badge"></a>
    <a href="https://lgtm.com/projects/g/tensorwerk/stockroom/"><img alt="lgtm" src="https://img.shields.io/lgtm/grade/python/github/tensorwerk/stockroom?style=for-the-badge"></a>
    <a href="https://github.com/psf/black"><img alt="lgtm" src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge"></a>
</p>

<p align="center">
    Version control for software 2.0
</p>


# Introduction
Stockroom is a platform to version models, data, parameters, experiment artifacts etc. alongside git
versioned source code.

- It is **easy**. The APIs are very similar to dictionaries in python
- It **works alongside Git** - in case you need to version source code as well. It's OK if you don't.
- **High performance**, thanks to the amazing [hangar](https://github.com/tensorwerk/hangar-py) library
- **Integration with PyTorch** and its ecosystem, so that you don't need to write the complex pipeline code.

# Why
One important motivation behind the initial design of stockroom is to avoid users
learning another tool for versioning. We try to make the APIs as minimal and familiar
as possible. Similar to other versioning tools, stockroom let "git" does ``checkout``
and rely on "git" to move between branches/commits. But unlike other tools, we channel
your data access through the smart API so that we don't need to move the huge data files
around when you traverse between commits.   


## Installation

<div class="termy">

```console
$ pip install stockroom
---> 100%
```

</div>



## Example
```Python hl_lines="3 4 8 14 15 16"
from stockroom import StockRoom

stock = StockRoom(write=True)
model.load_state_dict(stock.model['resnet50'])
for e in range(epochs):
    for i in range(limit):
        optimizer.zero_grad()
        x, y = stock.data['dataset_name', i]
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        if loss < previous_loss:
            stock.experiment['loss'] = loss.item()
            stock.model['resnet50'] = model.state_dict()
            stock.commit('adding a better model')
```

## Contributing

We'd love to have you in the contributors list. Do check out the [contribution guide](contributing.md) before submitting a PR.
Here is our latest #Hall-Of-Fame

[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/0)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/0)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/1)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/1)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/2)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/2)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/3)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/3)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/4)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/4)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/5)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/5)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/6)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/6)
[![](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/images/7)](https://sourcerer.io/fame/hhsecond/tensorwerk/stockroom/links/7)


## License

This project is licensed under the terms of the **Apache Software License 2.0**
