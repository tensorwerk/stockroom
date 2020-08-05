from torchvision import datasets
import numpy as np

from base import BaseImporter


class Cifar10(BaseImporter):

    def __init__(self, root='./', train=True):
        self.d = datasets.CIFAR10(root=root, train=train,
                                  download=True)
        self.sample_img, self.sample_label = self.d[0]
        self.sample_img = np.array(self.sample_img)
        self.sample_label = np.array([self.sample_label])

    def shape(self):
        return (self.sample_img.shape, self.sample_label.shape)

    def dtype(self):
        return (self.sample_img.dtype, self.sample_label.dtype)

    def __iter__(self):
        for img, label in self.d:
            img = np.array(img)
            label = np.array([label])
            yield (img, label)

    def is_variable(self):
        return False

    def __len__(self):
        return len(self.d)


class Mnist(BaseImporter):

    def __init__(self, root='./', train=True):
        self.d = datasets.MNIST(root=root, train=train,
                                download=True)
        self.sample_img, self.sample_label = self.d[0]
        self.sample_img = np.array(self.sample_img)
        self.sample_label = np.array([self.sample_label])

    def shape(self):
        return (self.sample_img.shape, self.sample_label.shape)

    def dtype(self):
        return (self.sample_img.dtype, self.sample_label.dtype)

    def __iter__(self):
        for img, label in self.d:
            img = np.array(img)
            label = np.array([label])
            yield (img, label)

    def is_variable(self):
        return False

    def __len__(self):
        return len(self.d)


class FashionMnist(BaseImporter):

    def __init__(self, root='./', train=True):
        self.d = datasets.FashionMNIST(root=root, train=train,
                                       download=True)
        self.sample_img, self.sample_label = self.d[0]
        self.sample_img = np.array(self.sample_img)
        self.sample_label = np.array([self.sample_label])

    def shape(self):
        return (self.sample_img.shape, self.sample_label.shape)

    def dtype(self):
        return (self.sample_img.dtype, self.sample_label.dtype)

    def __iter__(self):
        for img, label in self.d:
            img = np.array(img)
            label = np.array([label])
            yield (img, label)

    def is_variable(self):
        return False

    def __len__(self):
        return len(self.d)


datasets_configured = {
        'Cifar10': (Cifar10(train=True), Cifar10(train=False)),
        'Mnist': (Mnist(train=True), Mnist(train=False)),
        'FashionMnist': (FashionMnist(train=True), FashionMnist(train=True))
        }
