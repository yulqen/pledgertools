import csv
from typing import NamedTuple
import datetime


class LedgerLine(NamedTuple):
    """Represents a single line from hledger journal file."""
    date: datetime.date
    description: str
    transaction_type: str
    total: float


def parse(csv_file) -> None:
    r = []
    with open(csv_file, 'r') as cf:
        csv_reader = csv.reader(cf)
        for line in csv_reader:
            r.append(LedgerLine(
                line[0], line[1], line[2], float(line[3])))
        return r
