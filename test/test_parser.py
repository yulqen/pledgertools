import os
from tempfile import gettempdir
from datetime import date

import pytest


from pledgertools.pledger import parse

TMP_DIR = gettempdir()


@pytest.fixture
def journal_file() -> None:
    """
    Mocks a cleaned csv downloaded from HSBC.
    """
    with open(os.path.join(TMP_DIR, 'test_journal'), 'w') as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,-6.20\n")
        tf.write("28/06/2017,WWW.CALMAC.CO.UK INTERNET,VIS,-49.00\n")
        tf.write("28/06/2017,VODAFONE LTD,DD,-26.35\n")
        tf.write("27/06/2017,VIRGINTRAINSEC SER YORK 4400,VIS,-86.00\n")
    yield os.path.join(TMP_DIR, 'test_journal')
    os.unlink(os.path.join(TMP_DIR, 'test_journal'))


def test_date(journal_file) -> None:
    parsed = parse(journal_file)
    assert parsed[0].date == date(2017, 6, 28)
    assert parsed[3].date == date(2017, 6, 27)


def test_description(journal_file) -> None:
    parsed = parse(journal_file)
    assert parsed[0].description == "SAINSBURYS S/MKTS LONDON  SE12"
    assert parsed[1].description == "WWW.CALMAC.CO.UK INTERNET"
    assert parsed[2].description == "VODAFONE LTD"


def test_transaction_type(journal_file) -> None:
    parsed = parse(journal_file)
    assert parsed[0].transaction_type == "VIS"
    assert parsed[1].transaction_type == "VIS"
    assert parsed[2].transaction_type == "DD"


def test_cost_amount(journal_file) -> None:
    parsed = parse(journal_file)
    assert parsed[0].total == -6.20
    assert parsed[1].total == -49.00
    assert parsed[2].total == -26.35
    assert parsed[3].total == -86.00
