#!/usr/bin/env python3

with open('/home/lemon/Downloads/TransHist.csv', 'r', encoding='utf-8') as f:
    comma_count = 0
    for line in f.readlines():
        for char in line:
            if char == ",":
                comma_count += 1
        if comma_count != 3:
            print(line)
            comma_count = 0
        comma_count = 0
