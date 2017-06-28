import csv
from typing import NamedTuple
import datetime


class LedgerLine(NamedTuple):
    """Represents a single line from hledger journal file."""
    date: datetime.date
    description: str
    transaction_type: str
    total: float


def splat_date_str(d: str) -> datetime.date:
    """Converts a date string in format "dd/mm/yyyy" to a datetime.date obj."""
    d_list = d.split('/')
    return datetime.date(
        int(d_list[2]),
        int(d_list[1]),
        int(d_list[0]))


def parse(csv_file) -> list:
    with open(csv_file, 'r') as cf:
        csv_reader = csv.reader(cf)
        return [LedgerLine(
                    date=splat_date_str(line[0]),
                    description=line[1],
                    transaction_type=line[2],
                    total=float(line[3])) for line in csv_reader]
