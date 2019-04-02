def test_repr(loader):
    exps = loader.find_by_ids([1, 2])
    assert repr(exps) == "QuerySet([Experiment(id=1, name=example), Experiment(id=2, name=example)])"
