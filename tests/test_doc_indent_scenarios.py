import pytest


@pytest.mark.parametrize(
    "test_linter",
    [{"srcdir": "doc_test/doc_indent_scenarios"}],
    indirect=True,
)
def test_doc(test_linter):
    linter = test_linter
    assert 0 < len(linter.log)
    assert 1 == linter.files
    assert 5 == linter.errors
    warnings = [r for r in linter.caplog if r.levelname == "WARNING"]
    assert 5 == len(warnings)
