import os
import sys
import gzip
import json
import plyvel
import logging
import argparse
import internetarchive as ia

from tqdm import tqdm

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

    check_credentials()

    # open the database
    if args.db:
        db_path = args.db
    else:
        db_path = args.collection_id
    db = plyvel.DB(db_path, create_if_missing=True)

    if args.dump:
        dump(db)
        sys.exit()

    # determine how much work there is to do
    total_items = get_item_count(args.collection_id)
    total_items_saved = get_total_items_saved(db)

    # stop if it looks like we've got it all
    if total_items - total_items_saved == 0:
        logging.info('no new items in %s', args.collection_id)
        sys.exit()

    # configure a progress bar
    if total_items_saved > 0 and not args.fullscan:
        progress = tqdm(total=total_items - total_items_saved, unit='records')
        count = total_items_saved
    else:
        progress = tqdm(total=total_items, unit='records')
        count = 0

    stopped = False
    try:
        for item in get_items(args.collection_id, db, args.fullscan):
            progress.update(1)
            count += 1
    except KeyboardInterrupt:
        stopped = True
    finally:
        db.put(b'iacoll:count', bytes(str(count), 'utf8'))
        progress.close()
        db.close()

    if count != total_items and not stopped:
        print("\nIt looks like one of your previous runs failed to complete, please use --fullscan to synchronize.\n")

def check_credentials():
    session = ia.get_session()
    if session.access_key and session.secret_key:
        return
    print('I need your Internet Archive account login to fetch your API credentials. The username/password are not stored.')
    email = input('email address: ')
    password = input('password: ')
    ia.configure(email, password)

def get_item_count(coll_id):
    return len(ia.search_items('collection:%s' % coll_id))

def get_total_items_saved(db):
    return int(db.get(b'iacoll:count', 0))

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
        item_value = db.get(item_key)
        if item_value:
            logging.info('already saw %s', result['identifier'])
            yield(json.loads(item_value))
        else:
            item = ia.get_item(result['identifier'])
            db.put(item_key, bytes(json.dumps(item.item_metadata), 'utf8'))
            logging.info("saved %s", result['identifier'])
            yield(item.item_metadata)

    db.put(b'iacoll:last-item-id', bytes(new_last_id, 'utf8'))

def get_item_key(id):
    return bytes('iacoll:item:%s' % id, 'utf8')

def dump(db):
    for k, v in db.iterator(start=b'iacoll:item:', stop=b'iacoll:item;'):
        sys.stdout.write(v.decode('utf8') + '\n')

if __name__  == "__main__":
    main()
