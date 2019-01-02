# iacoll

*iacoll* allows you to regularly harvest the item metadata in an Internet
Archive collection and store it in a LevelDB database. The database is a
key/value store where the key is the unique Internet Archive item identifier,
and the value is the JSON for the item metadata.

For example you can download the metadata for items in the University of
Maryland's collection:

    % iacoll university_maryland_cp 

By default *iacoll* will create the LevelDB database in a directory named with
the item identifier. If you would like to control this you can explicitly pass
it:

    % iacoll university_maryland_cp --db /path/to/my/leveldb/database

When you run *iacoll* repeatedly it will look at the database and only fetch
newer records. If an update ever fails you may want to force a full scan:

    % iacoll university_maryland_cp --fullscan

If you would like to dump the metadata as line oriented JSON you can use --dump:

    % iacoll university_maryland_cp --dump > university_maryland_cp.jsonl

## Install

To install *iacoll* you'll first need to install Python and then:

    pip install iacoll
