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


class CocoCaptions(Torchvision):
    def __init__(self, root, ann_file):
        pass

    def __getitem__(self, index):
        img = np.random.random((640, 640, 3)).astype(np.uint8)
        captions = ["hai"] * 5
        return Image.fromarray(img), captions


class CocoDetection(Torchvision):
    def __init__(self, root, ann_file):
        pass

    def __getitem__(self, index):
        img = np.random.random((640, 640, 3)).astype(np.uint8)
        boxes = [{"bbox": [100, 100, 100, 100], "category_id": 0}]
        return Image.fromarray(img), boxes


class ImageFolder(Torchvision):
    def __init__(self, root):
        self.classes = []

    def __getitem__(self, index):
        img = np.random.random((500, 500, 3)).astype(np.uint8)
        return Image.fromarray(img), 0


class VOCSegmentation(Torchvision):
    def __init__(self, root, image_set, download):
        pass

    def __getitem__(self, index):
        img = np.random.random((500, 500, 3)).astype(np.uint8)
        seg = np.random.random((500, 500)).astype(np.uint8)
        return Image.fromarray(img), Image.fromarray(seg)


class VOCDetection(Torchvision):
    def __init__(self, root, image_set, download):
        pass

    def __getitem__(self, index):
        img = np.random.random((500, 500, 3)).astype(np.uint8)
        obj_dict = {
            "annotation": {
                "object": [
                    {
                        "name": "testname",
                        "bndbox": {
                            "xmin": "100",
                            "ymin": "100",
                            "xmax": "100",
                            "ymax": "100",
                        },
                    }
                ]
            }
        }
        return Image.fromarray(img), obj_dict
