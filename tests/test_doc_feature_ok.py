import pytest


@pytest.mark.parametrize(
    "test_linter",
    [{"srcdir": "doc_test/doc_features_ok"}],
    indirect=True,
)
def test_doc(test_linter):
    linter = test_linter
    assert 0 < len(linter.log)
    assert 0 == linter.errors
    assert 2 == linter.files
    warnings = [r for r in linter.caplog if r.levelname == "WARNING"]
    assert 0 == len(warnings)
