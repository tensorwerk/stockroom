# 🏃‍♀️ Quick Start

In this quick start guide, we'll

1. Import a torchvision dataset to stockroom
2. Train a CNN with this data
3. Save the experiment to stockroom for reproducibility
4. Save the model to stockroom and use it for deployment

## Install packages

<div class="termy">

```console
$ conda install pytorch torchvision cpuonly -c pytorch
---> 100%
$ pip install stockroom
---> 100%
```

</div>

## Import CIFAR10

<div class="termy">

```console
$ stock import torchvision.cifar10
Downloading cifar-10-python.tar.gz
---> 100%
Initializing stock repository
Adding cifar10 dataset to StockRoom 
---> 100%
Done!
```

</div>
