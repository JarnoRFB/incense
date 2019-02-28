from pytest import raises
from incense.experiment import Experiment


def test_find_by_id(loader):
    exp = loader.find_by_id(1)
    assert isinstance(exp, Experiment)
    assert exp.id == 1


def test_find_by_ids(loader):
    exps = loader.find_by_ids([1, 2])
    for exp in exps:
        assert isinstance(exp, Experiment)
    assert len(exps) == 2


def test_find_by_name(loader):
    exps = loader.find_by_name('example')
    assert len(exps) == 3


def test_find_by_key(loader):
    exps = loader.find_by_key('config.optimizer', 'adam')
    assert len(exps) == 1
    assert exps[0].config['optimizer'] == 'adam'


def test_find_by_str_config_key(loader):
    exps = loader.find_by_config_key('optimizer', 'adam')
    assert len(exps) == 1
    assert exps[0].config['optimizer'] == 'adam'


def test_find_by_number_config_key(loader):
    exps = loader.find_by_config_key('epochs', 3)
    assert len(exps) == 1
    assert exps[0].config['epochs'] == 3


def test_find(loader):
    exps = loader.find(
        {"$and": [
            {"config.optimizer": "sgd"},
            {"config.epochs": 3},
        ]}
    )
    assert len(exps) == 1
    assert exps[0].id == 2


def test_error_message_for_missing_id(loader):
    with raises(ValueError, match='Experiment with id 4 does not exist in database "incense_test".'):
        exp = loader.find_by_id(4)
