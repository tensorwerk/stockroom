from copy import deepcopy

import numpy as np
import pytest
import torch


def get_model():
    torch_model = torch.nn.Sequential(
        torch.nn.Linear(2, 3), torch.nn.ReLU(), torch.nn.Linear(3, 1)
    )
    return torch_model


# TODO: Ingore warning has no effect
@pytest.mark.filterwarnings("ignore:the imp module is deprecated:DeprecationWarning")
def test_saving_model(writer_stock):
    assert writer_stock.model.keys() == tuple()
    model = get_model()
    old_weights = model.state_dict()
    writer_stock.model["model"] = old_weights
    writer_stock.commit("adding model")
    assert writer_stock.model.keys() == ("model",)

    model = get_model()
    tmp_weights = deepcopy(model.state_dict())
    model.load_state_dict(writer_stock.model["model"])
    new_weights = deepcopy(model.state_dict())
    iterator = (
        old_weights.keys() if isinstance(old_weights, dict) else range(len(old_weights))
    )
    for k in iterator:
        assert np.allclose(old_weights[k], new_weights[k])
        assert not tmp_weights[k].sum() == 0.0 or np.allclose(
            tmp_weights[k], new_weights[k]
        )


def test_save_in_context_manager(reader_stock):
    assert reader_stock.model.keys() == tuple()
    model = get_model()
    with pytest.raises(AttributeError):  # TODO: should be a permission error
        reader_stock.model["model"] = model.state_dict()
    with reader_stock.enable_write():
        reader_stock.model["model"] = model.state_dict()
    assert reader_stock.model.keys() == ("model",)


def test_saving_two_models(writer_stock):
    model1 = get_model()
    model2 = get_model()
    weights1 = model1.state_dict()
    weights2 = model2.state_dict()
    writer_stock.model[1] = weights1
    writer_stock.model[2] = weights2
    writer_stock.commit("adding two models")
    ret_weights1 = writer_stock.model[1]
    ret_weights2 = writer_stock.model[2]
    model1.load_state_dict(ret_weights1)
    model2.load_state_dict(ret_weights2)
    iterator = (
        ret_weights1.keys()
        if isinstance(ret_weights1, dict)
        else range(len(ret_weights1))
    )
    for k in iterator:
        assert np.allclose(ret_weights1[k], weights1[k])
        assert np.allclose(ret_weights2[k], weights2[k])


def test_load_with_different_library_version(writer_stock, monkeypatch):
    model = get_model()
    writer_stock.model["model"] = model.state_dict()
    writer_stock.commit("adding model")
    with monkeypatch.context() as m:
        m.setattr(torch, "__version__", "0.111")
        with pytest.warns(UserWarning) as warning_rec:
            model.load_state_dict(writer_stock.model["model"])
        assert len(warning_rec) == 1
        assert "version used while storing the model" in warning_rec[0].message.args[0]


def test_unknown_model_type(writer_stock):
    with pytest.raises(TypeError):
        writer_stock.model["invalid"] = set()


def test_load_nonexisting_key(writer_stock):
    model = get_model()
    writer_stock.model["model"] = model.state_dict()
    writer_stock.commit("adding model")
    with pytest.raises(KeyError) as error:
        writer_stock.model["wrongname"]
    assert "Model with key wrongname not found" == error.value.args[0]
