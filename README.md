<div align="center">
  <img src="docs/img/logo_with_text.png" width="296" height="323">
  <br><br><br>
</div>


![Gitter](https://img.shields.io/gitter/room/tensorwerk/stockroom?color=%2332a877&style=for-the-badge)
[![PyPi](https://img.shields.io/pypi/v/stockroom?style=for-the-badge)](https://pypi.python.org/pypi/stockroom)
[![lgtm](https://img.shields.io/lgtm/grade/python/github/tensorwerk/stockroom?style=for-the-badge)](https://lgtm.com/projects/g/tensorwerk/stockroom/)

A version control system for software 2.0.

---

**Complete Documentation**: [stockroom.page](https://stockroom.page)

---

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
```python
from stockroom import StockRoom

stock = StockRoom()
weights = stock.model['resnet50']
model.load_state_dict(weights)
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

## Installation

```console
$ pip install stockroom
```

## Contributing
We'd love to have you in the contributors list. Do check out the [contributors guide]() before submitting a PR.
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
