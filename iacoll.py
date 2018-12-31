#!/usr/bin/env python3

"""
usage: iacoll <ia-collection-id> <gzip-file-path>

iacoll will collect all the item metadata for an Internet Archive collection
and store it as line-oriented json in a gzipped file.

If you run it more than once it will scan the gzipped file for the most recent
item and only append newer records.
"""

import os
import sys
import gzip
import json
import argparse
import internetarchive as ia

from dateutil.parser import parse

def main():
    ap = argparse.ArgumentParser('collect Internet Archive collectian metadata')
    ap.add_argument('collection_id', help='Internet Archive Collection ID')
    ap.add_argument('path', help='Path to write gzipped data to')
    args = ap.parse_args()

    last_id = get_last_id(args.coll)
    output = gzip.open(args.path, 'at')
    for item in get_new_items(last_id):
        m = item['metadata']['identifier']
        output.write(json.dumps(m) + '\n')
        print("saved %s [%s]" % (m['identifier'], m['addeddate']))

def get_new_items(last_id):
    for result in get_all_items():
        if result['identifier'] == last_id:
            break
        item = ia.get_item(result['identifier'])
        yield(item.item_metadata)

def get_last_id(path):
    if not os.path.isfile(path):
        return None
    last_id = None
    max_date = None
    for line in gzip.open(open(path, 'rb')):
        item = json.loads(line)
        if 'metadata' not in item or 'addeddate' not in item['metadata']:
            continue
        date = parse(item['metadata']['addeddate'])
        if max_date is None or date > max_date:
            max_date = date
            last_id = item['metadata']['identifier']
    return max_id

def get_all_items(coll_id):
    for item in ia.search_items('collection:%s' % coll_id,
            sorts=['addeddate desc']):
        yield item

if __name__  == "__main__":
    main()
