'''
Pytorch Dataloader into StockRoom
'''
from pathlib import Path
from typing import Union

from hangar import Repository
import numpy as np
from tqdm import tqdm
import torch
from torch.utils.data import Dataset

from stockroom import StockRoom


def hangar_transform(item):
    '''
    Converts a set of datatypes to numpy arrays that can be
    added to hangar
    '''
    if isinstance(item, torch.Tensor):
        return item.detach().numpy()
    if isinstance(item, int):
        return np.array([item])
    if isinstance(item, list):
        subsample = dict()
        for idx, i in enumerate(item):
            subsample[idx] = i
        return subsample

    return item


def add_from_dataset(           # pylint: disable='too-many-locals'
        name: str,
        dataset: Dataset,
        root_dir: Union[Path, str],
        column_postfixes: list = None
        ) -> str:
    '''
    Takes a dataset and adds it to StockRoom
    '''
    repo = Repository(root_dir)
    if not repo.initialized:
        print(f'The stock repo is not initialized in {root_dir}. Initializing...')
        uname = input('Username: ')
        uemail = input('Email: ')
        repo.init(user_name=uname, user_email=uemail)
        commit_hash = ''
        with open(Path(root_dir)/'head.stock', 'w+') as commit_file:
            commit_file.write(commit_hash)
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

    with stock.run():
        for i, sample in tqdm(enumerate(dataset), total=len(dataset),
                              position=0, leave=True):
            for column, item in zip(columns_added, sample):
                stock.data[column][i] = hangar_transform(item)

    stock.close()
