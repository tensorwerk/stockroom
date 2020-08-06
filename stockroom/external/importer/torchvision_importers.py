from torchvision import datasets
import numpy as np

from stockroom.external.importer.base import BaseImporter


class TorchvisionCommon(BaseImporter):

    def __init__(self, dataset, train):
        self.dataset = dataset
        self.split = 'train' if train else 'test'
        self.sample_img, self.sample_label = self.dataset[0]
        self.sample_img = np.array(self.sample_img)
        self.sample_label = np.array([self.sample_label])

    def column_names(self):
        return f'{self.name}-{self.split}-image', f'{self.name}-{self.split}-label'

    def shapes(self):
        return self.sample_img.shape, self.sample_label.shape

    def dtypes(self):
        return self.sample_img.dtype, self.sample_label.dtype

    def __iter__(self):
        for img, label in self.dataset:
            img = np.array(img)
            label = np.array([label])
            yield img, label

    def variability_status(self):
        return False

    def __len__(self):
        return len(self.dataset)


class Cifar10(TorchvisionCommon):
    name = 'cifar10'

    def __init__(self, root, train=True):
        dataset = datasets.CIFAR10(root=root, train=train, download=True)
        super().__init__(dataset, train)


class Mnist(TorchvisionCommon):
    name = 'mnist'

    def __init__(self, root, train=True):
        dataset = datasets.MNIST(root=root, train=train, download=True)
        super().__init__(dataset, train)


class FashionMnist(TorchvisionCommon):
    name = 'fashion_mnist'

    def __init__(self, root, train=True):
        dataset = datasets.FashionMNIST(root=root, train=train, download=True)
        super().__init__(dataset, train)
