import os
from collections import defaultdict

import numpy as np
from stockroom.external.importer.base import BaseImporter

try:
    from torchvision import datasets  # type: ignore
except ModuleNotFoundError:
    pass
import stockroom.external.importer.utils as utils
from rich.console import Console
from rich.table import Table


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
        return False

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


class ImageFolder(BaseImporter):
    name = "imagefolder"

    def __init__(self, root):
        try:
            self.dataset = datasets.ImageFolder(root)
        except FileNotFoundError:
            raise RuntimeError(
                f"Cannot find the directory '{os.path.expanduser(root)}'"
            )

        self.base_folder = os.path.expanduser(root).split("/")[-1]
        self.sample_img, self.sample_label = self._process_data(*self.dataset[0])

        self._gen_metadata()
        self._print_table()

    def column_names(self):
        return (
            f"{self.name}-{self.base_folder}-image",
            f"{self.name}-{self.base_folder}-label",
        )

    def shapes(self):
        return self.shape

    def dtypes(self):
        return self.sample_img.dtype, self.sample_label.dtype

    @classmethod
    def gen_splits(cls, root):
        return [cls(root)]

    def __iter__(self):
        for img, label in self.dataset:
            yield self._process_data(img, label)

    def __len__(self):
        return len(self.dataset)

    def variability_status(self):
        return True, False

    @staticmethod
    def _process_data(img, lbl):
        img = np.array(img)
        lbl = np.array(lbl)
        return img, lbl

    def _gen_metadata(self):
        print("Parsing data...")
        H = W = 0
        self.sample_counter = defaultdict(int)
        for img, lbl in self.dataset:
            # find max height/width
            h, w = img.size
            if h > H:
                H = h
            if w > W:
                W = w

            # find num samples in each class
            self.sample_counter[lbl] += 1
        _, _, c = self.sample_img.shape
        self.shape = ((W, H, c), self.sample_label.shape)

    def _print_table(self):
        table = Table(title="Sample Distribution")

        # columns
        table.add_column("Class Name")
        table.add_column("Number of samples", justify="right")

        # rows
        for class_label in self.dataset.classes:
            num_samples = self.sample_counter[self.dataset.class_to_idx[class_label]]
            table.add_row(str(class_label), str(num_samples))

        console = Console()
        console.print(table)


class COCO(BaseImporter):
    name = "coco"

    def __init__(self):
        urls = {
            "stockroom.zip": "https://github.com/tensorwerk/stockroom/archive/master.zip",
            # 'val': 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip',
            # 'test': 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip',
            "hangarboard.zip": "https://github.com/tensorwerk/hangarboard/archive/master.zip",
        }
        self.dest_dir = "/home/jamesjithin97/datasets/.stock"
        if not os.path.isdir(self.dest_dir):
            os.makedirs(self.dest_dir)

        utils.get_files(urls, self.dest_dir)

    def column_names(self):
        pass

    def shapes(self):
        pass

    def variability_status(self):
        pass

    def dtypes(self):
        pass

    def gen_splits(cls):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


class VOCSegmentation(BaseImporter):
    name = "voc_segmentation"

    def __init__(self, root, split):
        assert split in ["train", "trainval", "val"]
        self.split = split
        self.dataset = datasets.VOCSegmentation(root, image_set=split, download=True)
        self.sample_img, self.sample_seg = self._process_data(*self.dataset[0])

    def column_names(self):
        return f"{self.name}-{self.split}-image", f"{self.name}-{self.split}-segment"

    def shapes(self):
        return ((3, 500, 500), (500, 500))

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

    def __iter__(self):
        for img, seg in self.dataset:
            yield self._process_data(img, seg)

    def __len__(self):
        return len(self.dataset)

    @staticmethod
    def _process_data(img, seg):
        img = np.transpose(np.array(img), (2, 0, 1))
        img = np.ascontiguousarray(img)
        seg = np.ascontiguousarray(np.array(seg))

        return img, seg


class VOCDetection(BaseImporter):
    name = "voc_detection"

    def __init__(self, root, split):
        assert split in ["train", "trainval", "val"]
        self.split = split
        self.dataset = datasets.VOCDetection(root, image_set=split, download=True)
        self.sample_img, self.names, self.boxes = self._process_data(*self.dataset[0])

    def column_names(self):
        return (
            f"{self.name}-{self.split}-image",
            f"{self.name}-{self.split}-names",
            f"{self.name}-{self.split}-boxes",
        )

    def shapes(self):
        return ((3, 500, 500), None, self.boxes[0].shape)

    def dtypes(self):
        return self.sample_img.dtype, ["str"], [self.boxes[0].dtype]

    def variability_status(self):
        return True, True, True

    @classmethod
    def gen_splits(cls, root):
        dataset_splits = []
        for split in ["train", "trainval", "val"]:
            dataset_splits.append(cls(root, split))
        return dataset_splits

    def __iter__(self):
        for img, obj_dict in self.dataset:
            yield self._process_data(img, obj_dict)

    def __len__(self):
        return len(self.dataset)

    @staticmethod
    def _process_data(img, obj_dict):
        img = np.transpose(np.array(img), (2, 0, 1))
        img = np.ascontiguousarray(img)
        names = []
        bndboxes = []
        for obj in obj_dict["annotation"]["object"]:
            names.append(obj["name"])
            box = obj["bndbox"]
            bndboxes.append(
                (
                    (int(box["xmin"]), int(box["ymin"])),
                    (int((box["xmax"])), int(box["ymax"])),
                )
            )
        names = {i: name for i, name in enumerate(names)}
        bndboxes = {i: np.array(box) for i, box in enumerate(bndboxes)}
        return img, names, bndboxes
