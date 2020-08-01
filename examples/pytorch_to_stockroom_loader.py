import argparse
from pathlib import Path
from typing import Union

import torch
from torch.utils.data import Dataset
from torchvision import datasets, transforms
from stockroom import StockRoom, init_repo
from hangar import Repository
import numpy as np
from tqdm import tqdm

from dataset_configs import dataset_configs


def hangar_transform(item):
    if isinstance(item, torch.Tensor):
        return item.detach().numpy()
    if isinstance(item, int):
        return np.array([item])
    if isinstance(item, list):
        subsample = dict()
        for idx, i in enumerate(item):
            subsample[idx] = i
        return subsample


def add_from_dataset(
        name: str,
        dataset: Dataset,
        root_dir: Union[Path, str],
        column_postfixes: list = None
        ) -> str:

    repo = Repository(root_dir)
    if not repo.initialized:
        print(f'The stock repo is not initialized in {root_dir}. Initializing...')
        uname = input('Username: ')
        uemail = input('Email: ')
        repo.init(user_name=uname, user_email=uemail)
        commit_hash = ''
        with open(Path(root_dir)/'head.stock', 'w+') as f:
            f.write(commit_hash)
        print('StockRoom repo created')

    master = repo.checkout(write=True)

    # determine the columns to create
    sample = dataset[0]
    columns_added = []
    for i, column in enumerate(sample):

        if isinstance(column, int):
            prototype_int = np.array([column])
            column_name = f'{name}_{column_postfixes[i]}'
            columns_added.append(column_name)
            master.add_ndarray_column(
                column_name,
                prototype=prototype_int)
            print(f'Created Column: {column_name}')

        elif isinstance(column, torch.Tensor):
            numpy_col = column.detach().numpy()
            column_name = f'{name}_{column_postfixes[i]}'
            columns_added.append(column_name)
            master.add_ndarray_column(
                column_name,
                prototype=numpy_col)
            print(f'Created Column: {column_name}')

        elif isinstance(column, list):
            # nested columns
            if isinstance(column[0], str):
                column_name = f'{name}_{column_postfixes[i]}'
                columns_added.append(column_name)
                master.add_str_column(column_name,
                                      contains_subsamples=True)
                print(f'Created Subsampled-Column: {column_name}')

    # commit and close hangar repo
    master.commit('added columns'+str(columns_added))
    master.close()

    assert len(sample) == len(columns_added), f'{len(sample)} != {len(columns_added)}'
    # open stockroom
    stock = StockRoom(root_dir, write=True)

    with stock:
        with stock.run():
            for i, sample in tqdm(enumerate(dataset), total=len(dataset),
                                  position=0, leave=True):
                for column, item in zip(columns_added, sample):
                    stock.data[column][i] = hangar_transform(item)

def main(args):

    # build the config for the Dataset
    dataset_config = dataset_configs[args.dataset]
    if args.download_dir is False:
        args.download_dir = args.root
    d_names, kwargs = dataset_config.gen_kwargs(args.download_dir)

    datasets_configured = []
    for i, name in enumerate(d_names):
        d = datasets.__dict__[dataset_config.name](**kwargs[i])
        datasets_configured.append(d)

    # add to stockroom
    for i, d in enumerate(datasets_configured):
        add_from_dataset(d_names[i], d, args.root, ['img', 'label'])

    print(f'The {args.dataset} Dataset has been added to StockRoom.\nEnjoy!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset',
                        type=str,
                        choices=list(dataset_configs.keys()),
                        help='The name of PyTorch dataset you want to add to stockroom')

    parser.add_argument('--root',
                        type=str,
                        help='Root directory in which the dataset is downloaded to',
                        default='./')
    parser.add_argument('--download-dir', '-d',
                        default=False)

    args = parser.parse_args()
    main(args)
