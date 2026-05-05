from unittest.mock import patch

import pytest

import app.db as db_module


@pytest.fixture(autouse=True)
def isolated_db_global(tmp_path):
    """Redirect outcomes DB to tmp dir for all tests."""
    db_file = tmp_path / "test_outcomes.db"
    with patch.object(db_module, "_db_path", return_value=db_file):
        yield db_file
