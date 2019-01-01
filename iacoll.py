#!/usr/bin/env python3

"""
usage: iacoll <ia-collection-id>

iacoll will collect all the item metadata for an Internet Archive collection
and store it in a leveldb database. 

If you run it more than once with the same database it will only fetch records
since the last run.
"""

import os
import sys
import gzip
import json
import plyvel
import logging
import argparse
import internetarchive as ia

from tqdm import tqdm
from dateutil.parser import parse

def main():
    ap = argparse.ArgumentParser('collect Internet Archive collectian metadata')
    ap.add_argument('collection_id', help='Internet Archive Collection ID')
    ap.add_argument('--db', help='Location of leveldb database')
    ap.add_argument('--fullscan', action="store_true", help='Examine all search results, useful to fill in gaps if an update failed')
    ap.add_argument('--log', help='Path to write log', default='iacoll.log')
    args = ap.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    if args.db:
        db_path = args.db
    else:
        db_path = '%s.db' % args.coll_id

    db = plyvel.DB(db_path, create_if_missing=True)
    total_items = get_item_count(args.collection_id)
    total_items_saved = get_total_items_saved(db)

    if args.fullscan:
        progress = tqdm(total=total_items, unit='records')
        progress.update(total_items_saved)
    else:
        progress = tqdm(total=total_items - total_items_saved, unit='records')

    for item in get_items(args.collection_id, db, args.fullscan)
        progress.update(1)

    db.close()

def get_item_count(coll_id):
    return len(ia.search_items('collection:%s' % coll_id))

def get_total_items_saved(db):
    count + 0
    for k, v in db.iterator(start=b'iacoll:item:', end=b'iacoll:item;'):
        count += 1
    return count

def get_items(coll_id, db, last_id=None, fullscan=False):
    new_last_id = None
    for result in ia.search_items('collection:%s' % coll_id, sorts=['addeddate desc']):
        if new_last_id == None:
            new_last_id = result['identifier']

        if result['identifier'] == last_id and not fullscan:
            logging.info('found last id %s, stopping', last_id)
            break

        item_key = get_item_key(result['identifier'])
        if db.get(item_key):
            logging.info('already saw %s, skippping', result['identifier'])
            continue

        item = ia.get_item(result['identifier'])
        db.put(item_key, bytes(json.dump(item.item_metadata), 'utf8'))
        logging.info("saved %s" % item['metadata']['identifier'])

        yield(item.item_metadata)

    db.put('iacoll:last-item-id' % b(new_last_item_id, 'utf8'))

def get_item_key(id):
    return bytes('iacoll:item:%s' % id, 'utf8')

if __name__  == "__main__":
    main()
