import pytest
import numpy as np
from copy import deepcopy


class TestTFModelStore:

    @staticmethod
    def get_new_model():
        import tensorflow as tf
        tf_model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(3, activation='relu'),
            tf.keras.layers.Dense(1, activation='relu')
        ])
        tf_model.build((5, 2))
        return tf_model

    @pytest.mark.filterwarnings('ignore:the imp module is deprecated:DeprecationWarning')
    def test_saving_tf(self, stock):
        tf_model = self.get_new_model()
        old_weights = tf_model.get_weights()
        stock.model.save_weights('tf_model', tf_model)
        stock.commit("adding tf model")

        tf_model = self.get_new_model()
        tmp_weights = deepcopy(tf_model.get_weights())
        stock.model.load_weights('tf_model', tf_model)
        new_weights = deepcopy(tf_model.get_weights())
        for k in range(len(old_weights)):
            assert np.allclose(old_weights[k], new_weights[k])
            # bias is initiated as zero in tensorflow hence
            # the tmp and new both will be zero
            assert not tmp_weights[k].sum() == 0.0 \
                or np.allclose(tmp_weights[k], new_weights[k])


class TestTorchModelStore:

    @staticmethod
    def get_new_model():
        import torch
        torch_model = torch.nn.Sequential(
            torch.nn.Linear(2, 3),
            torch.nn.ReLU(),
            torch.nn.Linear(3, 1))
        return torch_model

    def test_saving_torch(self, stock):
        torch_model = self.get_new_model()
        old_state = torch_model.state_dict()
        stock.model.save_weights('torch_model', torch_model)
        stock.commit('adding torch model')

        torch_model = self.get_new_model()
        tmp_state = deepcopy(torch_model.state_dict())
        stock.model.load_weights('torch_model', torch_model)
        new_state = deepcopy(torch_model.state_dict())
        for k in old_state.keys():
            assert np.allclose(old_state[k], new_state[k])
            assert not np.allclose(tmp_state[k], new_state[k])

    def test_saving_two_models(self, stock):
        torch_model1 = self.get_new_model()
        torch_model2 = self.get_new_model()
        state1 = torch_model1.state_dict()
        state2 = torch_model2.state_dict()
        stock.model[1] = state1
        stock.model[2] = state2
        stock.commit('adding two models')
        ret_state1 = stock.model[1]
        ret_state2 = stock.model[2]
        torch_model1.load_state_dict(ret_state1)
        torch_model2.load_state_dict(ret_state2)
        for k in state1.keys():
            assert np.allclose(ret_state1[k], state1[k])
            assert np.allclose(ret_state2[k], state2[k])

    def test_load_with_different_library_version(self, stock, monkeypatch):
        import torch
        torch_model = self.get_new_model()
        stock.model.save_weights('thm', torch_model)
        stock.commit("adding th model")
        with monkeypatch.context() as m:
            m.setattr(torch, '__version__', '0.9')
            with pytest.warns(UserWarning) as warning_rec:
                stock.model.load_weights('thm', torch_model)
            assert len(warning_rec) == 1
            assert "PyTorch version used" in warning_rec[0].message.args[0]

    def test_unknown_model_type(self, stock):
        with pytest.raises(TypeError):
            stock.model.save_weights('invalid', {})

    def test_load_nonexisting_key(self, stock):
        thm = self.get_new_model()
        stock.model.save_weights('thm', thm)
        stock.commit("adding th model")
        with pytest.raises(KeyError) as error:
            stock.model.load_weights('wrongname', thm)
        assert 'Model with key wrongname not found' == error.value.args[0]
