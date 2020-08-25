import numpy as np
from PIL import Image


class Torchvision:
    def __len__(self):
        return 1

    def __iter__(self):
        yield self[0]


class CIFAR10(Torchvision):
    def __init__(self, root, train, download):
        pass

    def __getitem__(self, index):
        img = np.random.random((32, 32, 3)).astype(np.uint8)
        return Image.fromarray(img), index


class MNIST(Torchvision):
    def __init__(self, root, train, download):
        pass

    def __getitem__(self, index):
        img = np.random.random((28, 28)).astype(np.uint8)
        return Image.fromarray(img), 0


class FashionMNIST(Torchvision):
    def __init__(self, root, train, download):
        pass

    def __getitem__(self, index):
        img = np.random.random((28, 28)).astype(np.uint8)
        return Image.fromarray(img), 0


class VOCSegmentation(Torchvision):
    def __init__(self, root, image_set, download):
        pass

    def __getitem__(self, index):
        img = np.random.random((500, 500, 3)).astype(np.uint8)
        seg = np.random.random((500, 500)).astype(np.uint8)
        return Image.fromarray(img), Image.fromarray(seg)
