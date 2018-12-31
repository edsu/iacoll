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
import logging
import argparse
import internetarchive as ia

from tqdm import tqdm
from dateutil.parser import parse

def main():
    ap = argparse.ArgumentParser('collect Internet Archive collectian metadata')
    ap.add_argument('collection_id', help='Internet Archive Collection ID')
    ap.add_argument('path', help='Path to write gzipped data to')
    ap.add_argument('--log', help='Path to write log', default='iacoll.log')
    ap.add_argument('--resume', action="store_true", help='Resume failed update')
    args = ap.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    first_id, last_id, total_items_saved = get_archive_info(args.path)
    logging.info('found last id %s', last_id)
    logging.info('found first id %s', first_id)
    logging.info('found %s saved records', total_items_saved)
    total_items = get_item_count(args.collection_id)

    if args.resume:
        progress = tqdm(total=total_items, unit='records')
        progress.update(total_items_saved)
    else:
        progress = tqdm(total=total_items - total_items_saved, unit='records')

    output = gzip.open(args.path, 'at')
    for item in get_items(args.collection_id, first_id, last_id, args.resume):
        output.write(json.dumps(item) + '\n')
        progress.update(1)
        logging.info("saved %s" % item['metadata']['identifier'])

def get_item_count(coll_id):
    return len(ia.search_items('collection:%s' % coll_id))

def get_items(coll_id, first_id=None, last_id=None, resume=False):
    seen_first = False
    seen_last = False
    for result in ia.search_items('collection:%s' % coll_id, sorts=['addeddate desc']):
        if result['identifier'] == last_id:
            seen_last = True
        if result['identifier'] == first_id:
            seen_first = True

        if not resume and seen_last:
            break

        if resume and seen_last and not seen_first:
            continue

        item = ia.get_item(result['identifier'])
        yield(item.item_metadata)

def get_archive_info(path):
    if not os.path.isfile(path):
        return None, 0
    count = 0
    last_id = None
    first_id = None
    max_date = None
    min_date = None
    for line in gzip.open(open(path, 'rb')):
        count += 1
        item = json.loads(line)
        if 'metadata' not in item or 'addeddate' not in item['metadata']:
            continue
        date = parse(item['metadata']['addeddate'])
        if max_date is None or date > max_date:
            max_date = date
            last_id = item['metadata']['identifier']
        if min_date is None or date < min_date:
            min_date = date
            first_id = item['metadata']['identifier']
    return first_id, last_id, count

if __name__  == "__main__":
    main()
