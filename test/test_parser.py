import os

import pytest

from tempfile import gettempdir

from pledgertools.pledger import parse

TMP_DIR = gettempdir()


@pytest.fixture
def journal_file() -> None:
    """
    Mocks a hledger journal file.
    """
    with open(os.path.join(TMP_DIR, 'test_journal'), 'w') as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,-6.20")
    yield os.path.join(TMP_DIR, 'test_journal')
    os.unlink(os.path.join(TMP_DIR, 'test_journal'))


def test_cost_amount(journal_file) -> None:
    parsed = parse(journal_file)
    assert parsed[0].total == -6.20
