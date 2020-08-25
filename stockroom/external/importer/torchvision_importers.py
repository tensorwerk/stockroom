import numpy as np
from stockroom.external.importer.base import BaseImporter

try:
    from torchvision import datasets  # type: ignore
except ModuleNotFoundError:
    pass


class TorchvisionCommon(BaseImporter):
    def __init__(self, dataset, train):
        self.dataset = dataset
        self.split = "train" if train else "test"
        self.sample_img, self.sample_label = self._process_data(*self.dataset[0])

    def column_names(self):
        return f"{self.name}-{self.split}-image", f"{self.name}-{self.split}-label"

    def shapes(self):
        return self.sample_img.shape, self.sample_label.shape

    def dtypes(self):
        return self.sample_img.dtype, self.sample_label.dtype

    @staticmethod
    def _process_data(img, lbl):
        # TODO: memory copy
        img = np.array(img)
        img = img.astype(np.float32) / 255
        lbl = np.array(lbl)
        return img, lbl

    def __iter__(self):
        for img, label in self.dataset:
            yield self._process_data(img, label)

    def variability_status(self):
        return False, False

    def __len__(self):
        return len(self.dataset)

    @classmethod
    def gen_splits(cls, torchvision_dataset, root):
        dataset_splits = []
        for train in [True, False]:
            dataset = torchvision_dataset(root=root, train=train, download=True)
            dataset_splits.append(cls(dataset, train))
        return dataset_splits


class Cifar10(TorchvisionCommon):
    name = "cifar10"

    @classmethod
    def gen_splits(cls, root):
        return super().gen_splits(datasets.CIFAR10, root)

    @staticmethod
    def _process_data(img, lbl):
        img = np.transpose(np.array(img), (2, 0, 1))
        img = np.ascontiguousarray(img)
        img = img.astype(np.float32) / 255
        lbl = np.array(lbl)
        return img, lbl


class Mnist(TorchvisionCommon):
    name = "mnist"

    @classmethod
    def gen_splits(cls, root):
        return super().gen_splits(datasets.MNIST, root)


class FashionMnist(TorchvisionCommon):
    name = "fashion_mnist"

    @classmethod
    def gen_splits(cls, root):
        return super().gen_splits(datasets.FashionMNIST, root)


class VOCSegmentation(TorchvisionCommon):
    name = "voc_segmentation"

    def __init__(self, root, split):
        assert split in ["train", "trainval", "val"]
        self.split = split
        self.dataset = datasets.VOCSegmentation(root, image_set=split, download=True)
        self.sample_img, self.sample_seg = self._process_data(*self.dataset[0])

    def column_names(self):
        return f"{self.name}-{self.split}-image", f"{self.name}-{self.split}-segment"

    def shapes(self):
        return (3, 500, 500), (500, 500)

    def dtypes(self):
        return self.sample_img.dtype, self.sample_seg.dtype

    def variability_status(self):
        return True, True

    @classmethod
    def gen_splits(cls, root):
        dataset_splits = []
        for split in ["train", "trainval", "val"]:
            dataset_splits.append(cls(root, split))
        return dataset_splits

    @staticmethod
    def _process_data(img, seg):
        img = np.transpose(np.array(img), (2, 0, 1))
        img = np.ascontiguousarray(img)
        seg = np.ascontiguousarray(np.array(seg))
        return img, seg
