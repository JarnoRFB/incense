from incense import utils


def test_find_differing_config_keys(loader):
    assert utils.find_differing_config_keys(loader.find_by_ids([1, 2])) == {"epochs"}
    assert utils.find_differing_config_keys(loader.find_by_ids([1, 3])) == {"optimizer"}
    assert utils.find_differing_config_keys(loader.find_by_ids([2, 3])) == {"epochs", "optimizer"}


def test_format_config(loader):
    exp = loader.find_by_id(2)
    assert utils.format_config(exp, "epochs", "optimizer") == "epochs=3 | optimizer=sgd"
    assert utils.format_config(exp, "epochs") == "epochs=3"
