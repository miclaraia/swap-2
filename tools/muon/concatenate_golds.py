#!/usr/bin/env python

import csv
import argparse
import os

files = {0: 'muon_hunter_gold_false.csv',
         1: 'muon_hunter_gold_true.csv'}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Directory of muon gold csv files')
    parser.add_argument('out', help='Output gold data to file')

    args = parser.parse_args()
    path = args.dir

    path = os.path.abspath(path)

    out = args.out
    out = os.path.abspath(out)

    return path, out


def main():
    path, out = parse_args()

    data = {}
    for g, fname in files.items():
        fname = os.path.join(path, fname)

        with open(fname, 'r') as file:
            reader = csv.reader(file)

            for row in reader:
                s = int(row[0])
                data[s] = g

    headers = ['subject', 'gold']
    with open(out, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        writer.writeheader()
        for s in sorted(data):
            g = data[s]
            writer.writerow({'subject': s, 'gold': g})


if __name__ == '__main__':
    main()
