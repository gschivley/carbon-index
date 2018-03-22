#!/usr/bin/env python3


import argparse
import os
import csv
import re
import bisect
from collections import defaultdict, namedtuple


SENTENCE = ('{category} was {change} in {this_y} '
            '({this_v} {unit}) when compared to {prev_y} '
            '({prev_v} {unit}).')


Cat = namedtuple('Cat', ['name', 'field', 'unit', 'rows', 'tmpl'])


## Helpers
def calc_change_rate(x1, x2):
    return ((x2 - x1) / x1)

def format_num(num):
    return '{:.1f}'.format(num)

def format_rate(rate):
    """Format change rate into human friendly string."""
    rate_prcnt = rate * 100
    rank = bisect.bisect([-0.5, 0.5], rate_prcnt)
    tmpl = ['down by {}%',
            'flat',
            'up by {}%'][rank]
    return tmpl.format(format_num(abs(rate_prcnt)))


def extract_yq(yq_str):
    """Extract the year part and quarter part as two integers."""
    return [int(num) for num in re.findall(r'\d+', yq_str)]

def get_target_yq(y, q, rows):
    if y and q:
        return [y - 1, y], q
    elif q:
        ys = filter(lambda row: row['quarter'] == q, rows)
        ly = max(ys, key=lambda x: x['year'])['year']
        return [ly - 1, ly], q
    elif y:
        qs = filter(lambda row: row['year'] == y, rows)
        lq = max(qs, key=lambda x: x['quarter'])['quarter']
        return [y - 1, y], lq
    else:
        lr = max(rows, key=lambda x: x['year'] + x['quarter'] * 0.25)
        return [lr['year'] - 1, lr['year']], lr['quarter']

def process_row(row):
    """Convert one row into a better format."""
    return {**row, **dict(zip(['year', 'quarter'], extract_yq(row['year_quarter'])))}


## CLI
def is_valid_file(parser, filepath):
    if not os.path.exists(arg):
        parser.error('The file {} does not exist'.filepath)
    else:
        return filepath

def arg_parser():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(description='Generates release note for EmissionsIndex.org')
    parser.add_argument('qi',
            help='The quarterly emission index file.')
    parser.add_argument('qg',
            help='The quarterly generation file.')
    parser.add_argument('-y', '--year',
            type=int,
            help='The year of interest.')
    parser.add_argument('-q', '--quarter',
            type=int,
            help='The quarter of interest.')

    return parser.parse_args()


## Core
def read_file(filepath):
    """Read the csv file in."""
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        return [process_row(row) for row in reader]

def get_desired_two_rows(args, rows):
    """Get the two rows of interest."""
    ys, q = get_target_yq(args.year , args.quarter, rows)
    qs = list(filter(lambda x: x['quarter'] == q, rows))
    helper = lambda y: next(filter(lambda x: x['year'] == y, qs))
    return [helper(y) for y in ys]

def compare(prev_y, this_y, field):
    """Compare this year with previous year."""
    rate = calc_change_rate(float(prev_y[field]), float(this_y[field]))
    return {'this_y': this_y['year_quarter'],
            'this_v': format_num(float(this_y[field])),
            'prev_y': prev_y['year_quarter'],
            'prev_v': format_num(float(prev_y[field])),
            'change': format_rate(rate)}

def summarize(args, cat):
    """Summarize data into human readable sentences."""
    ys = get_desired_two_rows(args, cat.rows)
    contents = compare(*ys, cat.field)
    return cat.tmpl.format(category=cat.name, unit=cat.unit,
                            **contents)


## Run
if __name__ == '__main__':
    args = arg_parser()
    qi = read_file(args.qi)
    qg = read_file(args.qg)

    qg_cat_rows = defaultdict(list)
    for row in qg:
        qg_cat_rows[row['fuel category']].append(row)

    cats = [Cat('The Power Sector Carbon Index',
                'index (g/kwh)',
                'g/kWh',
                qi,
                SENTENCE),
            *[Cat('{} generation'.format(key),
                  'generation (M MWh)',
                  'million MWh',
                  qg_cat_rows[key],
                  SENTENCE) for key in qg_cat_rows.keys()]]

    with open(os.path.join('website csv', 'blog.txt'), 'w') as f:
        f.write('\n\n'.join(map(lambda x: summarize(args, x), cats)))
    f.close()
    # print('\n\n'.join(map(lambda x: summarize(args, x), cats)))
