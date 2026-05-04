import pytest


@pytest.mark.parametrize(
    "test_linter",
    [{"srcdir": "doc_test/doc_indent_4", "indent": 4}],
    indirect=True,
)
def test_doc(test_linter):
    linter = test_linter
    assert 0 < len(linter.log)
    assert 1 == linter.files
    assert 0 == linter.errors
    warnings = [r for r in linter.caplog if r.levelname == "WARNING"]
    assert 0 == len(warnings)
