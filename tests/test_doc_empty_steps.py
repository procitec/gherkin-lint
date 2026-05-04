import pytest


@pytest.mark.parametrize(
    "test_linter",
    [{"srcdir": "doc_test/doc_empty_steps"}],
    indirect=True,
)
def test_doc(test_linter):
    linter = test_linter
    assert 0 < len(linter.log)
    assert 3 == linter.files
    assert 4 == linter.errors
    warnings = [r for r in linter.caplog if r.levelname == "WARNING"]
    assert 4 == len(warnings)
