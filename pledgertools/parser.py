import csv
import datetime
import re
import unicodedata
from reprlib import repr
from typing import NamedTuple, Iterable, List
from enum import Enum, auto

journal_date_regex = re.compile(
    r"^(?P<year>\d{4})?[\/\-\.]?(?P<month>\d{2})[\/\.\-](?P<day>\d{1,2})"
)

DATE = r"(?P<DATE>(?P<year>\d{4})+[\/\-\.]?(?P<month>\d{2})[\/\.\-](?P<day>\d{1,2}))"
NL = r"(?P<NL>\n)"
WS = r"(?P<WS>\s+)"
ST = r"(?P<ST>\*)"
WORD = r"(?P<WORD>\w+)"
NEG = r"(?P<NEG>\-)"
COLON = r"(?P<COLON>:)"
PRICE = r"(?P<PRICE>(?P<currency>[\u00a3])?(P=NEG)?\d+(?:\.\d{1,2})?)"

master_pat = re.compile("|".join([NEG, NL, DATE, PRICE, COLON, WS, ST, WORD]))


class TransactionType(Enum):
    EXPENSE = auto
    INCOME = auto


TRANSACTION_DESCRIPTORS = {
    "SAINSBURYS S/MKTS LONDON  SE12": (
        "Sainsbury's Food Shopping",
        "Expenses:Food:Groceries",
        TransactionType.EXPENSE,
    )
}


class Token(NamedTuple):
    type: str
    value: str


"""
What follows is the use of re.scanner(), which is undocumented. I got this from the Python 3 Cookbook.
See: https://stackoverflow.com/questions/37075691/method-regex-scanner-cannot-be-found-in-the-python-3-5-1-documentation-but-th
You might read this in the future, at which point `scanner()` has been
removed by `finditer()`.
"""


def generate_tokens(text) -> Iterable:
    for m in master_pat.finditer(text):
        yield Token(m.lastgroup, m.group())


def detect_currency_symbol(journal_str: str) -> bool:
    parsed = [s for s in journal_str if unicodedata.category(s) == "Sc"]
    if len(parsed) > 0:
        return True
    else:
        return False


class Transaction:
    """
    A Journal comprises many listed Transactions, each of which describes the transaction in terms
    of date, description, type, status. Each transaction involves zero or more "postings"
    http://hledger.org/manual.html#journal-format
    """

    def __init__(self, date: str, status: str, code: str, description: str):
        self.date = splat_date_str(date)
        self.date_str = date
        self.status = status
        self.code = code
        self.description = description
        self.postings = []

    def __repr__(self):
        return repr(f"<Transaction: {self.date_str} - {self.description}")


class BankCSVLine(NamedTuple):
    """Represents a single line in a CSV file downloaded from the bank."""

    date: datetime.date
    description: str
    transaction_type: str
    total: float

    def __repr__(self):
        return f"<BankCVSLine - {self.date}: {self.description}, {self.transaction_type} -> {self.total}>"


def splat_date_str(d: str) -> datetime.date:
    """Converts a date string in format "dd/mm/yyyy" to a datetime.date obj."""
    d_list = d.split("/")
    return datetime.date(int(d_list[2]), int(d_list[1]), int(d_list[0]))


def parse_csv(csv_file) -> List[BankCSVLine]:
    """
    Parses the CSV file made available at HSBC (following cleaning) into
    a list of BankCSVLine objects which hold data about the transaction.
    """
    with open(csv_file, "r", encoding="utf8") as cf:
        csv_reader = csv.reader(cf)
        return [
            BankCSVLine(
                date=splat_date_str(line[0]),
                description=line[1],
                transaction_type=line[2],
                total=float(line[3]),
            )
            for line in csv_reader
        ]


def date_format_checker(date: str) -> bool:
    """
    Given a date in 'yyyy/mm/dd', 'yyyy.mm.dd' or 'yyyy-mm-dd' format,
    checks whether the date is a valid one.
    :param date:
    :return: bool
    """
    m = re.match(journal_date_regex, date)
    if m:
        if int(m.group("month")) <= 12:
            if m.group("month") in [
                "1",
                "01",
                "3",
                "03",
                "5",
                "05",
                "7",
                "07",
                "8",
                "08",
                "10",
                "12",
            ]:
                if not int(m.group("day")) <= int("31"):
                    return False
            if m.group("month") in ["4", "04", "6", "06", "9", "09", "11"]:
                if not int(m.group("day")) <= int("30"):
                    return False
            if m.group("month") in ["2", "02"]:
                if m.group("day") not in ["28", "29"]:
                    return False
        else:
            return False
    return True


def parse_journal(journal_file) -> list:
    pass


def total_formatter(parsed_csv_line: BankCSVLine) -> str:
    total = str(parsed_csv_line.total)
    if TRANSACTION_DESCRIPTORS[parsed_csv_line[1]][2] == TransactionType.EXPENSE:
        return "".join(["??", total[1:]])
    else:
        return "".join(["??", total])


def journal_from_parsed_csv_line(parsed_csv_line: BankCSVLine) -> str:
    class JournalEntry(NamedTuple):
        date: datetime.date
        description_line: str
        middle_line: str

    description_line = " ".join(
        [
            "/".join(
                [
                    str(parsed_csv_line.date.day),
                    str(parsed_csv_line.date.month),
                    str(parsed_csv_line.date.year),
                ]
            ),
            "*",
            TRANSACTION_DESCRIPTORS[parsed_csv_line[1]][
                0
            ],  # looking for SAINBURYS S/MKTS LONDON  SE12
        ]
    )

    middle_line = "".join(
        [
            TRANSACTION_DESCRIPTORS[parsed_csv_line[1]][1],
            "\t",
            str(total_formatter(parsed_csv_line)),
        ]
    )

    return JournalEntry(
        date=parsed_csv_line.date,
        description_line=description_line,
        middle_line=middle_line,
    )
