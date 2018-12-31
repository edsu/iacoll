# iacoll

*iacoll* will collect all the item metadata for an Internet Archive collection
and store it as line-oriented json in a gzipped file.

For example you can download the metadata for items in the University of
Maryland's collection:

    % iacoll university_maryland_cp university_maryland_cp.jsonl.gz

If you run it more than once it will scan the gzipped file for the most recent
item and only append newer records.

## Install

To install iacoll you'll first need to install Python and then:

    pip install iacoll
