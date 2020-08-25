import numpy as np
from stockroom import console


def test_columns_added():
    splits_added = {"train": ["test_column", 1]}
    console.print_columns_added(splits_added)


def test_experiment_tags():
    tags = {"test_tag": 0.01}
    console.print_experiment_tags(tags)


def test_data_summary():
    column_info = [("test_col", 1, (1, 2), np.int64)]
    console.print_data_summary(column_info)


def test_model_table():
    model = "test_model"
    console.print_models_table(model)
