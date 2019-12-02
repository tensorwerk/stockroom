import torch
import numpy as np
from stockroom import ModelStore
import stockroom


def get_torch_model():
    torch_model = torch.nn.Sequential(
        torch.nn.Linear(2, 3),
        torch.nn.ReLU(),
        torch.nn.Linear(3, 1))
    return torch_model


def get_tf_model():
    pass


def test_saving_torch(repo):
    modelstore = ModelStore()

    torch_model = get_torch_model()
    old_state = torch_model.state_dict()
    modelstore.save('torch_model', torch_model)
    stockroom.commit('adding torch model')

    torch_model = get_torch_model()
    tmp_state = torch_model.state_dict()
    modelstore.load('torch_model', torch_model)
    new_state = torch_model.state_dict()
    for k in old_state.keys():
        assert np.allclose(old_state[k], new_state[k])
