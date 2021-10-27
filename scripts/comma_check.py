#!/usr/bin/env python3

import sys

if sys.argv[-1].split("/")[-1] != "TransHist.csv":
    print("Target file must be TransHist.csv")
    sys.exit(1)

with open(sys.argv[-1], "r", encoding="utf-8") as f:
    comma_count = 0
    for line in f.readlines():
        for char in line:
            if char == ",":
                comma_count += 1
        if comma_count != 3:
            print(line)
            comma_count = 0
        comma_count = 0
