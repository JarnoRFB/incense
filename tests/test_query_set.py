from pytest import raises
from sacred import Experiment as SacredExperiment


def test_repr(loader):
    exps = loader.find_by_ids([1, 2])
    assert repr(exps) == "QuerySet([Experiment(id=1, name=example), Experiment(id=2, name=example)])"


def test_delete(delete_db_loader, delete_mongo_observer, capsys):
    add_exp_to_db(delete_mongo_observer, config_value=1)
    add_exp_to_db(delete_mongo_observer, config_value=2)

    # Retrieve and delete experiment.
    exps = delete_db_loader.find_by_ids([1, 2])
    exps.delete(confirmed=True)
    captured = capsys.readouterr()
    assert captured.out.split("\n")[-2] == "Deleted 2 experiments"
    assert exps.data == []

    # Make sure experiment cannot be retrieved again.
    with raises(ValueError):
        exp = delete_db_loader.find_by_id(1)
    with raises(ValueError):
        exp = delete_db_loader.find_by_id(2)


def add_exp_to_db(delete_mongo_observer, config_value):
    ex = SacredExperiment("name")
    ex.observers.append(delete_mongo_observer)
    ex.add_config({"value": config_value})

    def run(value, _run):
        _run.log_scalar("test_metric", 1)
        _run.add_artifact(__file__)
        return value

    ex.main(run)
    ex.run()


def test_delete_prompt(loader, monkeypatch, capsys):
    """Check that experiment is not deleted if prompt is answered with 'N'."""
    exps = loader.find_by_ids([1, 2])
    with monkeypatch.context() as m:
        m.setattr("builtins.input", lambda x: "N")
        exps.delete()
    captured = capsys.readouterr()
    assert captured.out == "Deletion aborted\n"
    exps = loader.find_by_ids([1, 2])
    assert exps[0].id == 1
    assert exps[1].id == 2
