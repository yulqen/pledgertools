import os
import re
from tempfile import gettempdir
from datetime import date

import pytest

import pledgertools.pledger as pledger

TMP_DIR = gettempdir()


@pytest.fixture
def cleaned_csv_file() -> None:
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


@pytest.fixture
def incorrect_first_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, 'test_journal'), 'w') as tf:
        tf.write("2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,WRONG\n")
    yield os.path.join(TMP_DIR, 'test_journal')
    os.unlink(os.path.join(TMP_DIR, 'test_journal'))


@pytest.fixture
def incorrect_second_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, 'test_journal'), 'w') as tf:
        tf.write("28/06/2017,23.1,SAINSBURYS S/MKTS LONDON  SE12,VIS,-6.20\n")
    yield os.path.join(TMP_DIR, 'test_journal')
    os.unlink(os.path.join(TMP_DIR, 'test_journal'))


@pytest.fixture
def incorrect_third_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, 'test_journal'), 'w') as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,20,VIS,-6.20\n")
    yield os.path.join(TMP_DIR, 'test_journal')
    os.unlink(os.path.join(TMP_DIR, 'test_journal'))


@pytest.fixture
def incorrect_fourth_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, 'test_journal'), 'w') as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,WRONG\n")
    yield os.path.join(TMP_DIR, 'test_journal')
    os.unlink(os.path.join(TMP_DIR, 'test_journal'))

@pytest.fixture
def journal() -> None:
    with open(os.path.join(TMP_DIR, 'test_ledger_journal'), 'w') as tf:
        tf.write("""
        2017/06/30 Zipadee Celery Ltd
            expenses:gifts                      12.90
            assets:hsbc current                 -12.90
        """)

def test_date(cleaned_csv_file) -> None:
    parsed = pledger.parse_csv(cleaned_csv_file)
    assert parsed[0].date == date(2017, 6, 28)
    assert parsed[3].date == date(2017, 6, 27)


def test_description(cleaned_csv_file) -> None:
    parsed = pledger.parse_csv(cleaned_csv_file)
    assert parsed[0].description == "SAINSBURYS S/MKTS LONDON  SE12"
    assert parsed[1].description == "WWW.CALMAC.CO.UK INTERNET"
    assert parsed[2].description == "VODAFONE LTD"


def test_transaction_type(cleaned_csv_file) -> None:
    parsed = pledger.parse_csv(cleaned_csv_file)
    assert parsed[0].transaction_type == "VIS"
    assert parsed[1].transaction_type == "VIS"
    assert parsed[2].transaction_type == "DD"


def test_cost_amount(cleaned_csv_file) -> None:
    parsed = pledger.parse_csv(cleaned_csv_file)
    assert parsed[0].total == -6.20
    assert parsed[1].total == -49.00
    assert parsed[2].total == -26.35
    assert parsed[3].total == -86.00


def test_first_field_is_not_date(incorrect_first_field) -> None:
    with pytest.raises(IndexError):
        pledger.parse_csv(incorrect_first_field)


def test_second_field_is_wrong_type(incorrect_second_field) -> None:
    with pytest.raises(ValueError):
        pledger.parse_csv(incorrect_second_field)


def test_third_field_is_wrong_type(incorrect_third_field) -> None:
    with pytest.raises(ValueError):
        pledger.parse_csv(incorrect_third_field)


def test_fourth_field_is_wrong_type(incorrect_fourth_field) -> None:
    with pytest.raises(ValueError):
        pledger.parse_csv(incorrect_fourth_field)

def test_journal_date_regex():
    d_reg = re.match(pledger.journal_date_regex, '2016/06/30')
    assert d_reg

def test_bad_date():
    assert not pledger.date_format_checker('2016/13/01')
    assert not pledger.date_format_checker('2016/20/03')
    assert not pledger.date_format_checker('2016/12/32')
    assert not pledger.date_format_checker('2016/14/32')

def test_good_date():
    assert pledger.date_format_checker('2016/01/01')
    assert pledger.date_format_checker('2016/02/29')

def test_good_month_bad_day():
    assert not pledger.date_format_checker('2016/02/30')
    assert not pledger.date_format_checker('2017/04/31')

#def test_date_field_from_journal_file(journal) -> None:
#   parsed = pledger.parse_journal(journal)
#   assert parsed[0].date == date(2017, 6, 30)
