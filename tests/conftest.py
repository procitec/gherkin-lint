"""Pytest conftest module containing common test configuration and fixtures."""

# import shutil
# from pathlib import Path
from datetime import datetime
import glob
from pathlib import Path
import pytest
from gherkin_lint.gherkin_lint import GherkinLint, OutputManager


class TestLinter:
    log = ""

    def __init__(self, log, errors, files, caplog):
        self.log = log
        self.errors = errors
        self.files = files
        self.caplog = caplog


@pytest.fixture()
def test_linter(request, caplog, tmp_path):
    log = ""
    total_errors = 0
    linter_params = request.param

    srcdir = Path(__file__).parent.absolute() / linter_params.get("srcdir")

    assert srcdir.exists()

    indent = linter_params.get("indent", 2)

    with caplog.at_level("WARNING"):
        # Setup output management
        indent_size = indent
        files = [Path(f) for f in glob.glob(f"{srcdir}/*.feature")]
        print(srcdir)
        print(files)

        logfile = tmp_path / "linter.log"

        output_manager = OutputManager(logfile=logfile, verbosity=2)
        logger = output_manager.logger

        # Log execution start
        logger.info(f"Gherkin Feature File Linter started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Indentation depth: {indent_size}")
        logger.info(f"Files to check: {len(files)}")

        linter = GherkinLint(indent_size=indent_size, logger=logger)

        total_errors = 0
        processed = 0

        for path in files:
            if not path.exists():
                logger.error(f"Error: File {path} does not exist")
                continue
            logger.debug(f"Linting file: {path}")
            errors = linter.lint_file(path)
            output_manager.print_results(path, errors)
            total_errors += len(errors)
            processed += 1

        output_manager.print_summary(total_errors, processed)

        with open(logfile) as _f:
            log = _f.read().splitlines()

    print(f"caplog records {caplog.records}")
    return TestLinter(log, total_errors, processed, caplog.records)
