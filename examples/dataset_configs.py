from torchvision import transforms

# the various types of dataset found in torchvision
VISION_DATA_TYPES = {
    'classification': list(('MNIST FashionMNIST KMNIST EMNIST QMNIST' +
                            'FakeData LSUM ImageFolder DatasetFolder' +
                            'ImageNet CIFAR10 CIFAR100 STL10 SVHN' +
                            'USPS').split(' ')),
    'captioning': list('CocoCaptions Flickr8k Flickr30k'.split(' ')),
    #'detection': list('')
    'segmentation': list('VOCSegmentation SBDataset'.split(' ')),
    'action_reco': list('UCF101 HMDB51 Kinetics400'.split(' ')),
}

VISION_COLUMN_NAMES = {
    'classification': ('image', 'label'),
    'captioning': ('image', 'caption'),
    #'detection': None,
    'segmentation': ('image', 'segmentedImage'),
    'action_reco': ('video', 'audio', 'label')
}


class DatasetConfig:
    def __init__(self,
                 name,
                 transform=transforms.ToTensor(),
                 target_transform=None,
                 train_arg=False,
                 splits=None,
                 split_arg_name='split',
                 downloadable=True,
                 special_args=None):

        self.name = name
        self.downloadable = downloadable
        self.transform = transform
        self.target_transform = target_transform
        self.train_arg = train_arg
        if train_arg:
            self.splits = ('train', 'test')
        elif splits is not None:
            self.splits = splits
        else:
            self.splits = None
        self.split_arg_name = split_arg_name
        self.special_args = special_args

    def __len__(self):
        if self.splits is not None:
            return len(self.splits)
        else:
            return 0

    def gen_kwargs(self, root_dir):
        kwargs = {}
        kwargs['root'] = root_dir
        if self.downloadable:
            kwargs['download'] = True
        if self.transform:
            kwargs['transform'] = self.transform
        if self.target_transform:
            kwargs['target_transform'] = self.target_transform
        if self.special_args is not None:
            kwargs.update(self.special_args)

        dataset_names = []
        if self.__len__() > 0:
            kwargs_list = []
            if self.train_arg:
                kwargs['train'] = True
                kwargs_list.append(kwargs.copy())
                dataset_names.append(f'{self.name}_train')
                kwargs['train'] = False
                kwargs_list.append(kwargs.copy())
                dataset_names.append(f'{self.name}_test')
            else:
                for split in self.splits:
                    kwargs[self.split_arg_name] = split
                    kwargs_list.append(kwargs.copy())
            kwargs = kwargs_list

        return dataset_names, kwargs

# TorchVision Datasets
# TODO add VOC, COCO
mnist = DatasetConfig('MNIST', train_arg=True)
cifar10 = DatasetConfig('CIFAR10', train_arg=True)
fashion_mnist = DatasetConfig('FashionMNIST', train_arg=True)

resize = transforms.Compose([
                    transforms.Resize([224, 224]),
                    transforms.ToTensor(),])
image_folder = DatasetConfig('ImageFolder',
                             transform=resize,
                             splits=None,
                             downloadable=False)
voc_seg = DatasetConfig('VOCSegmentation',
                        transform=resize,
                        target_transform=resize,
                        split_arg_name='image_set',
                        splits=['train', 'val', 'trainval'])

def voc_target_transform(target):
    col_dict = {}
    target = target['annotation']
    size = target['size']
    size = (int(size['height']), int(size['width']), int(size['depth']))
    col_dict['size'] = size
    bndbox_objs = []
    bndbox_cords = []
    objects = target['object']
    for obj in objects:
        bndbox_objs.append(obj['name'])
        bndbox = obj['bndbox']
        cords = (int(bndbox['xmin']), int(bndbox['ymin']),
                 int(bndbox['xmax']), int(bndbox['ymax']))
        bndbox_cords.append(cords)

    col_dict['objects'] = bndbox_objs
    col_dict['boxes'] = bndbox_cords
    return col_dict

voc_det = DatasetConfig('VOCDetection',
                        transform=resize,
                        target_transform=voc_target_transform,
                        split_arg_name='image_set',
                        splits=['train', 'val', 'trainval'])

dataset_configs = {
        'Mnist': mnist,
        'Cifar10': cifar10,
        'Fashion-mnist': fashion_mnist,
        'ImageFolder': image_folder,
        'VOCSegmentation': voc_seg,
        'VOCDetection': voc_det,
        }
