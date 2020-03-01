import pytest
import numpy as np
from copy import deepcopy

import torch
import tensorflow as tf


def get_torch_model():

    torch_model = torch.nn.Sequential(
        torch.nn.Linear(2, 3),
        torch.nn.ReLU(),
        torch.nn.Linear(3, 1))
    return torch_model, torch_model.state_dict, torch_model.load_state_dict


def get_tf_model():
    tf_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(3, activation='relu'),
        tf.keras.layers.Dense(1, activation='relu')
    ])
    tf_model.build((5, 2))
    return tf_model, tf_model.get_weights, tf_model.set_weights


# TODO: Ingore warning has no effect
@pytest.mark.parametrize('get_model', [get_tf_model, get_torch_model])
@pytest.mark.filterwarnings('ignore:the imp module is deprecated:DeprecationWarning')
def test_saving_model(stock, get_model):
    model, weight_getter, weight_setter = get_model()
    old_weights = weight_getter()
    stock.model.save_weights('model', model)
    stock.commit('adding model')

    model, weight_getter, weight_setter = get_model()
    tmp_weights = deepcopy(weight_getter())
    stock.model.load_weights('model', model)
    new_weights = deepcopy(weight_getter())
    iterator = old_weights.keys() if isinstance(old_weights, dict) else range(len(old_weights))
    for k in iterator:
        assert np.allclose(old_weights[k], new_weights[k])
        # bias is initiated as zero in tensorflow hence
        # the tmp and new both will be zero
        assert not tmp_weights[k].sum() == 0.0 \
            or np.allclose(tmp_weights[k], new_weights[k])


@pytest.mark.parametrize('get_model', [get_torch_model, get_tf_model])
def test_saving_two_models(stock, get_model):
    model1, weight_getter1, weight_setter1 = get_model()
    model2, weight_getter2, weight_setter2 = get_model()
    weights1 = weight_getter1()
    weights2 = weight_getter2()
    stock.model[1] = weights1
    stock.model[2] = weights2
    stock.commit('adding two models')
    ret_weights1 = stock.model[1]
    ret_weights2 = stock.model[2]
    weight_setter1(ret_weights1)
    weight_setter2(ret_weights2)
    iterator = ret_weights1.keys() if isinstance(ret_weights1, dict) else range(len(ret_weights1))
    for k in iterator:
        assert np.allclose(ret_weights1[k], weights1[k])
        assert np.allclose(ret_weights2[k], weights2[k])


@pytest.mark.parametrize('get_model', [get_torch_model, get_tf_model])
def test_load_with_different_library_version(stock, monkeypatch, get_model):
    model, weight_getter, weight_setter = get_model()
    stock.model.save_weights('model', model)
    stock.commit("adding model")
    with monkeypatch.context() as m:
        m.setattr(torch, '__version__', '0.111')
        m.setattr(tf, '__version__', '0.111')
        with pytest.warns(UserWarning) as warning_rec:
            stock.model.load_weights('model', model)
        assert len(warning_rec) == 1
        assert "version used while storing the model" in warning_rec[0].message.args[0]


def test_unknown_model_type(stock):
    with pytest.raises(TypeError):
        stock.model.save_weights('invalid', {})


@pytest.mark.parametrize('get_model', [get_torch_model, get_tf_model])
def test_load_nonexisting_key(stock, get_model):
    model, weight_getter, weight_setter = get_model()
    stock.model.save_weights('model', model)
    stock.commit("adding model")
    with pytest.raises(KeyError) as error:
        stock.model.load_weights('wrongname', model)
    assert 'Model with key wrongname not found' == error.value.args[0]
