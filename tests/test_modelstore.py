import pytest
import numpy as np
import stockroom
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
    def test_saving_tf(self, repo):
        modelstore = stockroom.modelstore(write=True)

        tf_model = self.get_new_model()
        old_weights = tf_model.get_weights()
        modelstore.save('tf_model', tf_model)
        stockroom.commit("adding tf model")

        tf_model = self.get_new_model()
        tmp_weights = deepcopy(tf_model.get_weights())
        modelstore.load('tf_model', tf_model)
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

    def test_saving_torch(self, repo):
        modelstore = stockroom.modelstore(write=True)

        torch_model = self.get_new_model()
        old_state = torch_model.state_dict()
        modelstore.save('torch_model', torch_model)
        stockroom.commit('adding torch model')

        torch_model = self.get_new_model()
        tmp_state = deepcopy(torch_model.state_dict())
        modelstore.load('torch_model', torch_model)
        new_state = deepcopy(torch_model.state_dict())
        for k in old_state.keys():
            assert np.allclose(old_state[k], new_state[k])
            assert not np.allclose(tmp_state[k], new_state[k])

    def test_saving_with_read_only_store(self, repo):
        modelstore = stockroom.modelstore()
        torch_model = self.get_new_model()
        with pytest.raises(PermissionError):
            modelstore.save('torch_model', torch_model)

    def test_load_with_different_library_version(self, repo, monkeypatch):
        import torch
        modelstore = stockroom.modelstore(write=True)
        torch_model = self.get_new_model()
        modelstore.save('thm', torch_model)
        stockroom.commit("adding th model")
        with monkeypatch.context() as m:
            m.setattr(torch, '__version__', '0.9')
            with pytest.warns(UserWarning) as warning_rec:
                modelstore.load('thm', torch_model)
            assert len(warning_rec) == 1
            assert "PyTorch version used" in warning_rec[0].message.args[0]

    def test_unknown_model_type(self, repo):
        modelstore = stockroom.modelstore(write=True)
        with pytest.raises(TypeError):
            modelstore.save('invalid', {})

    def test_load_nonexisting_key(self, repo):
        modelstore = stockroom.modelstore(write=True)
        thm = self.get_new_model()
        modelstore.save('thm', thm)
        stockroom.commit("adding th model")
        with pytest.raises(KeyError) as error:
            modelstore.load('wrongname', thm)
        assert 'Model with key wrongname not found' == error.value.args[0]

    def test_saving_model_while_another_write_operation(self, repo):
        co = stockroom.datastore(write=True)
        modelstore = stockroom.modelstore(write=True)
        thm = self.get_new_model()
        with pytest.raises(PermissionError) as error:
            modelstore.save('thm', thm)
        assert "Could not acquire the lock" in error.value.args[0]
