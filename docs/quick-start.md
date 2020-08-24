# 🏃‍♀️ Quick Start

Eager to take a quick run through stockroom? This page gives a good and crisp introduction to stockroom.

1. Import a cifar10 dataset from torchvision to stockroom
2. Train a CNN with this data
3. Save the hyper parameters and model to stockroom for reproducibility

You need to install `stockroom`, `pytorch`, `torchvision` and `matplotlib` for this tutorial

!!! tip "Use conda"
    installing pytorch and torchvision using pypi might install the `manylinux` bundle which is huge
    in size. Use conda if you can


## Introduction

Stockroom exposes the environment as three shelves. Data, Model and Experiments. This segregation let
stockroom to be prejudice about what goes inside and optimize the storage. Stockroom also introduces
`stock` CLI which gives you the ability to interact with your stockroom repository in a git-like way.
Checkout the [reference doc](cli.md) for complete CLI reference. You'll be using both the CLI and
Python APIs of stockroom in this tutorial. 

## Initialize Stock Repository

`CD` to your project directory and initialize it as a `stock` repository

<div class="termy">

```console
$ stock init --username myname --email a@b.c
---> 100%
```

</div>


## Import CIFAR10

StockRoom keeps all your data in `.data` shelf arranged as columns. In our case, data is imported as four columns.

- Train images
- Train labels
- Test images
- Test labels

!!! info "Data is Tensor"
    Stockroom makes strong assumptions about your data. Any data point that goes into stockroom must be
    a tensor a.k.a `numpy.ndarray` object. It is why stockroom could optimize the data storage
    and versioning efficiently. Also, know that, this philosophy is originally from Hangar and we use
    Hangar internally for all type of storages 

<div class="termy">

```console
$ stock import torchvision.cifar10
Downloading cifar-10-python.tar.gz
---> 100%
Adding cifar10 dataset to StockRoom 
---> 100%
Done!
```

</div>

Once you have the CIFAR data downloaded and added to your stock repository, you can create your project files and start
building the network. We are using the [CIFAR10 example](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)
from pytorch's blitz tutorial here, with few modification to load the data from stockroom instead of torchvision.

!!! tip "Stockroom is better off with git"
    Stockroom is designed to be able work without git but git will enable you to track your source code along with machine
    learning artifacts and data


## Build The Model

We'll build a simple CNN model as given in the pytorch tutorial

```python
import torch.nn as nn
import torch.nn.functional as F 

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
```

## Exploring data

Stockroom gives you simple, dictionary-like APIs for accessing and storing things. You'd create a `stock`
object that gives you the access to the storage

```python hl_lines="1 10"
from stockroom import StockRoom
import matplotlib.pyplot as plt
import numpy as np

def imshow(img):
    plt.imshow(np.transpose(img, (1, 2, 0)))
    plt.show()


stock = StockRoom()
index = 100
img = stock.data['cifar10-train-image'][index]
imshow(img)
```

!!! info "Read Access"
    Making `stock` object as given above will only give you a read enabled object. For saving data, you'd need
    to open the `enable_write` context manager or create the `stock` object by enabling write mode.
    ```python
    stock = StockRoom()
    with stock.enable_write():
        write_into(stock)
    # or
    stock = StockRoom(enable_write=True)
    write_into(stock)
    ```
    You'll see an example below

### Accessing data

As you already know, data is stored as columns inside the `.data` shelf in stockroom. You can get fetch the column
from the `.data` attribute and then fetch the data at a particular index - here we take the 100th data point.

```python hl_lines="12"
from stockroom import StockRoom
import matplotlib.pyplot as plt
import numpy as np

def imshow(img):
    plt.imshow(np.transpose(img, (1, 2, 0)))
    plt.show()


stock = StockRoom()
index = 100
img = stock.data['cifar10-train-image'][index]
imshow(img)
```

!!! tip "Column Names"
    You need to know the column names to interact with the data in the `.data` shelf.
    These names will be printed to the terminal when you import data. But if you
    missed/forget them, use 
    ```python
    stock.data.keys()
    ```

## DataLoader

Making a PyTorch DataLoader for your data is possible with the `make_torch_dataset` function. It
takes `columns` as first argument in a python list/tuple and gives you the element from each column
on a particular index

!!! info
    `make_torch_dataset` is a Hangar function and stockroom only exposing it for convenience

### Make Dataset

```python hl_lines="1 7"
from stockroom import make_torch_dataset
from torch.utils.data import DataLoader


imgcol = stock.data['cifar10-train-image']
lblcol = stock.data['cifar10-train-label']
dset = make_torch_dataset([imgcol, lblcol])
dloader = DataLoader(dset, batch_size=64)
```


### Make DataLoader

The dataset returned from `make_torch_dataset` is a subclass of `torch.utils.data.Dataset` and
hence is understood by torch `DataLoader`. You could create the dataloader as you create with
any dataset. Huge batch size, custom collate function, multiple threads - doesn't matter. Use
it as you wish. Remember, you have made a read only `stock` object, you'd never corrupt your
data with that.

```python hl_lines="8"
from stockroom import make_torch_dataset
from torch.utils.data import DataLoader


imgcol = stock.data['cifar10-train-image']
lblcol = stock.data['cifar10-train-label']
dset = make_torch_dataset([imgcol, lblcol])
dloader = DataLoader(dset, batch_size=64)
```


## Training

We'll open a write enabled `stock` object here since we need to store experiment information (hyper parameters,
metrics, output, artifacts etc) and model to stockroom.

!!! warning "Careful with the `write` access"
    With more power comes more responsibility. Remember, you can write to your repository

!!! success "Your data is safe"
    With the power of hangar, any data that is committed to stockroom is safe there. Even if you overwrite
    that data in a new commit, you can always time travel to previous commit and access your old data 


### Store hyper-parameters

As `.data` shelf store your data, hyper-parameters and experiment artifacts must be stored in the
`.experiment` shelf. While the `.data` shelf only allow you to store tensor data, `.experiment` shelf
will eventually allow you to store any artificats, like a loss graph, or a pickled file you'd need
for training your model etc.

```python hl_lines="14 15 16"
for epoch in range(2):
    p = tqdm(dloader)
    for i, (inputs, labels) in enumerate(p):
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if i % check_every == check_every - 1:
            current_loss = running_loss / check_every
            running_loss = 0.0
            if current_loss < best_loss:
                with stock.enable_write(commit_msg=f"{best_loss=}"):
                    stock.experiment['lr'] = lr
                    stock.experiment['momentum'] = momentum
                    stock.model['cifarmodel'] = net.state_dict()
                best_loss = current_loss
```

### Store model

The `.model` shelf takes `state_dict` from a pytorch model and nothing else. You will eventually be able to store
a `jit`ed model into your `.experiment` store but `.model` shelf is designed to store your model weights passed
as a dictionary.

```python hl_lines="14 17"
for epoch in range(2):
    p = tqdm(dloader)
    for i, (inputs, labels) in enumerate(p):
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if i % check_every == check_every - 1:
            current_loss = running_loss / check_every
            running_loss = 0.0
            if current_loss < best_loss:
                with stock.enable_write(commit_msg=f"{best_loss=}"):
                    stock.experiment['lr'] = lr
                    stock.experiment['momentum'] = momentum
                    stock.model['cifarmodel'] = net.state_dict()
                best_loss = current_loss
```

!!! tip "Storing weights is better"
    As far as you version your source code, saving the weights is always better. We are building more utilities,
    especially visualization tools, to interact with the data in stockroom. This will eventually help you to analyze
    the model weights, visualize them and even diff it 🤯😍

### Commit your changes

Commit your changes as you move forward, you can always time travel back and look at. With the context
managers, `autocommit` is enabled by default. You can control this behaviour by changing the argument
value
`.data` or `.experiment` or `.model` shelves

```python hl_lines="14"
for epoch in range(2):
    p = tqdm(dloader)
    for i, (inputs, labels) in enumerate(p):
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        if i % check_every == check_every - 1:
            current_loss = running_loss / check_every
            running_loss = 0.0
            if current_loss < best_loss:
                with stock.enable_write(commit_msg=f"{best_loss=}"):
                    stock.experiment['lr'] = lr
                    stock.experiment['momentum'] = momentum
                    stock.model['cifarmodel'] = net.state_dict()
                best_loss = current_loss
```

!!! info "stock commit != git commit"
    Stock commit is not same as a git commit. In fact, you can combine multiple stock commit in one
    git commit and consider that as an experiment


## Recap

- Initialize stock repository
- Import torchvision dataset to the repository
- Build the network
- Train your network
- Add data, augment it, experiment with hyper parameters but commit to stockroom along with you commit your source code

In case you need, the source code for the above experiment is available at the github repository
[hhsecond/stockroom-cifar10](https://github.com/hhsecond/stockroom-cifar10)
