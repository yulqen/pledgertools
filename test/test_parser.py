import os
import re
from datetime import date
from tempfile import gettempdir

import pytest

import pledgertools.parser as parser

TMP_DIR = gettempdir()

JOURNAL_ENTRY = (
    "2017/07/05 * Tiger stuff\n"
    "expenses:joanna business:materials                  12.00\n"
    "assets:hsbc current                                 -12.0\n"
)
JOURNAL_ENTRY2 = (
    "2017/07/06 * McDonalds LUNCH\n"
    "expenses:food:fast food                              £5.99\n"
    "assets:hsbc current                                 £-5.99\n"
)

MERGED_JOURNAL = "\n".join([JOURNAL_ENTRY, JOURNAL_ENTRY2])


@pytest.fixture
def cleaned_csv_file() -> None:
    """
    Mocks a cleaned csv downloaded from HSBC.
    """
    with open(os.path.join(TMP_DIR, "test_journal"), "w") as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,-6.20\n")
        tf.write("28/06/2017,WWW.CALMAC.CO.UK INTERNET,VIS,-49.00\n")
        tf.write("28/06/2017,VODAFONE LTD,DD,-26.35\n")
        tf.write("27/06/2017,VIRGINTRAINSEC SER YORK 4400,VIS,-86.00\n")
    yield os.path.join(TMP_DIR, "test_journal")
    os.unlink(os.path.join(TMP_DIR, "test_journal"))


@pytest.fixture
def incorrect_first_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, "test_journal"), "w") as tf:
        tf.write("2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,WRONG\n")
    yield os.path.join(TMP_DIR, "test_journal")
    os.unlink(os.path.join(TMP_DIR, "test_journal"))


@pytest.fixture
def incorrect_second_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, "test_journal"), "w") as tf:
        tf.write("28/06/2017,23.1,SAINSBURYS S/MKTS LONDON  SE12,VIS,-6.20\n")
    yield os.path.join(TMP_DIR, "test_journal")
    os.unlink(os.path.join(TMP_DIR, "test_journal"))


@pytest.fixture
def incorrect_third_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, "test_journal"), "w") as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,20,VIS,-6.20\n")
    yield os.path.join(TMP_DIR, "test_journal")
    os.unlink(os.path.join(TMP_DIR, "test_journal"))


@pytest.fixture
def incorrect_fourth_field() -> None:
    """
    Mocks a cleaned csv file downloaded from HSCB but includes fields that
    are the incorrect type.
    """
    with open(os.path.join(TMP_DIR, "test_journal"), "w") as tf:
        tf.write("28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,WRONG\n")
    yield os.path.join(TMP_DIR, "test_journal")
    os.unlink(os.path.join(TMP_DIR, "test_journal"))


@pytest.fixture
def journal() -> None:
    f = os.path.join(TMP_DIR, "test_ledger_journal")
    with open(f, "w") as tf:
        tf.write(
            """
        2017/06/30 Zipadee Celery Ltd
            expenses:gifts                      12.90
            assets:hsbc current                 -12.90
        """
        )
        tf.write(MERGED_JOURNAL)
    yield f
    os.unlink(f)


def test_date(cleaned_csv_file) -> None:
    parsed = parser.parse_csv(cleaned_csv_file)
    assert parsed[0].date == date(2017, 6, 28)
    assert parsed[3].date == date(2017, 6, 27)


def test_description(cleaned_csv_file) -> None:
    parsed = parser.parse_csv(cleaned_csv_file)
    assert parsed[0].description == "SAINSBURYS S/MKTS LONDON  SE12"
    assert parsed[1].description == "WWW.CALMAC.CO.UK INTERNET"
    assert parsed[2].description == "VODAFONE LTD"


def test_transaction_type(cleaned_csv_file) -> None:
    parsed = parser.parse_csv(cleaned_csv_file)
    assert parsed[0].transaction_type == "VIS"
    assert parsed[1].transaction_type == "VIS"
    assert parsed[2].transaction_type == "DD"


def test_cost_amount(cleaned_csv_file) -> None:
    parsed = parser.parse_csv(cleaned_csv_file)
    assert parsed[0].total == -6.20
    assert parsed[1].total == -49.00
    assert parsed[2].total == -26.35
    assert parsed[3].total == -86.00


def test_first_field_is_not_date(incorrect_first_field) -> None:
    with pytest.raises(IndexError):
        parser.parse_csv(incorrect_first_field)


def test_second_field_is_wrong_type(incorrect_second_field) -> None:
    with pytest.raises(ValueError):
        parser.parse_csv(incorrect_second_field)


def test_third_field_is_wrong_type(incorrect_third_field) -> None:
    with pytest.raises(ValueError):
        parser.parse_csv(incorrect_third_field)


def test_fourth_field_is_wrong_type(incorrect_fourth_field) -> None:
    with pytest.raises(ValueError):
        parser.parse_csv(incorrect_fourth_field)


def test_journal_date_regex() -> None:
    d_reg = re.match(parser.journal_date_regex, "2016/06/30")
    assert d_reg


def test_bad_date() -> None:
    assert not parser.date_format_checker("2016/13/01")
    assert not parser.date_format_checker("2016/20/03")
    assert not parser.date_format_checker("2016/12/32")
    assert not parser.date_format_checker("2016/14/32")


def test_good_date() -> None:
    assert parser.date_format_checker("2016/01/01")
    assert parser.date_format_checker("2016/02/29")


def test_good_month_bad_day() -> None:
    assert not parser.date_format_checker("2016/02/30")
    assert not parser.date_format_checker("2017/04/31")


def test_token_parse_text_types() -> None:
    p = parser.generate_tokens(JOURNAL_ENTRY)
    assert next(p).type == "DATE"
    assert next(p).type == "WS"
    assert next(p).type == "ST"
    assert next(p).type == "WS"
    assert next(p).type == "WORD"
    assert next(p).type == "WS"
    assert next(p).type == "WORD"
    assert next(p).type == "NL"
    assert next(p).type == "WORD"
    assert next(p).type == "COLON"
    assert next(p).type == "WORD"
    assert next(p).type == "WS"
    assert next(p).type == "WORD"
    assert next(p).type == "COLON"
    assert next(p).type == "WORD"
    assert next(p).type == "WS"
    assert next(p).type == "PRICE"


def test_token_parse_text_values() -> None:
    p = parser.generate_tokens(JOURNAL_ENTRY)
    assert next(p).value == "2017/07/05"
    assert next(p).value == " "
    assert next(p).value == "*"
    assert next(p).value == " "
    assert next(p).value == "Tiger"
    assert next(p).value == " "
    assert next(p).value == "stuff"
    assert next(p).value == "\n"
    assert next(p).value == "expenses"
    assert next(p).value == ":"
    assert next(p).value == "joanna"
    assert next(p).value == " "
    assert next(p).value == "business"


def test_token_parse_negative_currency() -> None:
    p = parser.generate_tokens(JOURNAL_ENTRY2)
    pl = list(p)
    assert pl[-1] == parser.Token(type="NL", value="\n")


def test_detect_currency_symbol() -> None:
    """
    TODO: Tests needed for all these...
    http://www.fileformat.info/info/unicode/category/Sc/list.htm.
    :return:
    """
    p = "£5.99"
    d = "$4.32"
    e = "\u20ac69.34"  # EURO symbol
    ps = "\u20b1200.23"  # Peso symbol
    assert parser.detect_currency_symbol(p) == True
    assert parser.detect_currency_symbol(d) == True
    assert parser.detect_currency_symbol(e) == True
    assert parser.detect_currency_symbol(ps) == True


def test_merged_journal() -> None:
    p = parser.generate_tokens(MERGED_JOURNAL)
    pl = list(p)
    assert True  # TODO finish this test


def test_create_journal_entry_from_csv_line(cleaned_csv_file) -> None:
    """
    This is the line I want to parse:
    28/06/2017,SAINSBURYS S/MKTS LONDON  SE12,VIS,-6.20

    It should return:
    28/6/21 * Sainsbury's Food Shopping
    Expenses:Food:Groceries             £6.20
    Assets:MyBank:Current

    given the additional variables, somewhere:
        cleared = True (the asterisk)
        SAINSBURYS S/MKTS LONDON  SE12 found to match Sainsbur's Food Shopping
        bucket = True (removing the need to explicitly balance
    """
    parsed = parser.parse_csv(cleaned_csv_file)
    journal_entry = parser.journal_from_parsed_csv_line(parsed[0])
    # First line of journal
    assert journal_entry.date == date(2017, 6, 28)
