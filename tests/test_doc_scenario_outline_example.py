import pytest


@pytest.mark.parametrize(
    "test_linter",
    [{"srcdir": "doc_test/doc_scenario_outline_example"}],
    indirect=True,
)
def test_doc(test_linter):
    linter = test_linter
    assert 0 < len(linter.log)
    assert 3 == linter.errors
    assert 4 == linter.files
    warnings = [r for r in linter.caplog if r.levelname == "WARNING"]
    assert 3 == len(warnings)
