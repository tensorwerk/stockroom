from typing import Union
from pathlib import Path

from torchvision import transforms, datasets


class DatasetConfig:
    '''
    Dataset config object to generate the kwargs for a given dataset.
    '''
    def __init__(self,                      # pylint: disable='too-many-arguments'
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
        return 0

    def gen_kwargs(self, root_dir: Union[str, Path]):
        '''
        Generate the kwargs for the DatasetConfig.
        '''
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
        if len(self) > 0:
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
                    dataset_names.append(f'{self.name}_{split}')
            kwargs = kwargs_list

        return dataset_names, kwargs


# TorchVision Datasets
# TODO add COCO
# TODO test VOC and ImageFolder
mnist = DatasetConfig('MNIST', train_arg=True)
cifar10 = DatasetConfig('CIFAR10', train_arg=True)
fashion_mnist = DatasetConfig('FashionMNIST', train_arg=True)

resize = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor()])
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
    'Custom transform for VOC Object-detection target dictionary'

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


def gen_datasets(dataset_name: str, download_dir: Union[str, Path]):
    '''
    Generate a list of configured datasets.
    '''
    # build the config for the Dataset
    dataset_config = dataset_configs[dataset_name]

    d_names, kwargs = dataset_config.gen_kwargs(download_dir)

    datasets_configured = []
    for i, name in enumerate(d_names):
        d = datasets.__dict__[dataset_config.name](**kwargs[i])
        datasets_configured.append(d)

    return d_names, datasets_configured

