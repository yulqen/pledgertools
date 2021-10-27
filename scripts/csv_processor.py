#!/usr/bin/env python3

import codecs
import re
import sys

outfile = open("hsbc_cleaned.csv", "w")

if sys.argv[-1].split("/")[-1] != "TransHist.csv":
    print("Target file must be TransHist.csv")
    sys.exit(1)


with open(sys.argv[-1], encoding="utf-8-sig") as f:
    bom_length = len(codecs.BOM_UTF8)
    for line in f.readlines():
        line = re.sub(r"\s{3,}", ",", line)
        line = re.sub(r'"', "", line)
        line = re.sub(r",,", ",", line)
        # line = re.sub(r",(?!(VIS|\)\)\)|ATM))", " ", line)
        line = re.sub(r"(?<=(2017|2018|2019|2020)) ", ",", line)
        line = re.sub(r" (?=(-|-\d.\.|\d.\.))", ",", line)
        line = re.sub(r" (?=CR)", ",", line)
        line = re.sub(r" (?=DD)", ",", line)
        line = re.sub(r" (?=BP)", ",", line)
        line = re.sub(r" (?=SO)", ",", line)
        line = re.sub(r" (?=VIS)", ",", line)
        line = re.sub(r",- ", "", line)
        line = re.sub(r",-,", ",", line)
        line = re.sub(r"CR ", "CR,", line)
        line = re.sub(r"VIS ", "VIS,", line)
        line = re.sub(r"Fee DR", "Fee,DR", line)
        line = re.sub(r"(?<=USD),", " ", line)
        line = re.sub(r"(?<=\d) (?=\d+\.\d{2})", "", line)
        line = re.sub(r"([a-zA-Z]),([a-zA-Z])", r"\1 \2", line)
        outfile.write(line)
outfile.close()
print(f"Written {outfile.name} successfully.")
