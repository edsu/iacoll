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
    ap.add_argument('--dump', action='store_true', help='Dump metadata in db to stdout')
    args = ap.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    if args.db:
        db_path = args.db
    else:
        db_path = args.collection_id

    db = plyvel.DB(db_path, create_if_missing=True)
    total_items = get_item_count(args.collection_id)
    total_items_saved = get_total_items_saved(db)

    if args.dump:
        dump(db)
        sys.exit()

    if total_items - total_items_saved == 0:
        logging.info('no new items in %s', args.collection_id)
        sys.exit()

    if args.fullscan:
        progress = tqdm(total=total_items, unit='records')
        progress.update(total_items_saved)
    else:
        progress = tqdm(total=total_items - total_items_saved, unit='records')

    try:
        for item in get_items(args.collection_id, db, args.fullscan):
            progress.update(1)
    except KeyboardInterrupt:
        pass

    progress.close()
    db.close()

def get_item_count(coll_id):
    return len(ia.search_items('collection:%s' % coll_id))

def get_total_items_saved(db):
    count = 0
    for k, v in db.iterator(start=b'iacoll:item:', stop=b'iacoll:item;'):
        count += 1
    return count

def get_items(coll_id, db, fullscan=False):
    last_id = db.get(b'iacoll:last-item-id', b'').decode('utf8')
    logging.info('found last item id %s', last_id)
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
        db.put(item_key, bytes(json.dumps(item.item_metadata), 'utf8'))
        logging.info("saved %s", result['identifier'])

        db.put(b'iacoll:last-item-id', bytes(new_last_id, 'utf8'))
        yield(item.item_metadata)

def get_item_key(id):
    return bytes('iacoll:item:%s' % id, 'utf8')

def dump(db):
    for k, v in db.iterator(start=b'iacoll:item:', stop=b'iacoll:item;'):
        sys.stdout.write(v.decode('utf8') + '\n')

if __name__  == "__main__":
    main()
