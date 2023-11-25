import argparse
import os
import time
from multiprocessing import Pool

from funcs import DataBase, parse_item

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db", type=str, default="../assets/iclr2024.db", help="path to database file"
    )
    parser.add_argument(
        "--suf", type=int, default=0, help="suffix of column to operate"
    )
    parser.add_argument(
        "--nproc",
        type=int,
        default=None,
        help="number of processor for multiprocessing",
    )
    parser.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()

    db = DataBase(args.db)
    db.initialize(create=False)

    # add new column
    try:
        db.cursor.execute(f"ALTER TABLE submissions ADD COLUMN r_{args.suf}_cnt int")
        db.cursor.execute(f"ALTER TABLE submissions ADD COLUMN r_{args.suf}_avg float")
        db.cursor.execute(f"ALTER TABLE submissions ADD COLUMN r_{args.suf}_std float")
        db.cursor.execute(f"ALTER TABLE submissions ADD COLUMN r_{args.suf} text")
        print(f"Creat column with suffix: {args.suf} successfully.")
    except:
        print(
            f"Column with suffix: {args.suf} existed already, passing without create new columns."
        )

    # fetch all items for loop
    # db.cursor.execute('SELECT id, url FROM submissions')
    # data = db.cursor.fetchall()
    # db.close()

    # fetch all data from txt
    with open("../assets/id_list.txt", "r") as f:
        data = f.readlines()
    data = data[:40] if args.debug else data

    # multiprocessing to parse metadata of each item
    p = Pool(processes=args.nproc)
    num_items = len(data)
    print(
        f"Processing {num_items} items with {os.cpu_count() if args.nproc is None else args.nproc} processes:"
    )
    start = time.time()
    for i in range(num_items):
        url = data[i].strip()
        url = f"https://openreview.net/forum?id={url}"
        # parse_item(i, args.suf, url, args.db)
        p.apply_async(parse_item, args=(i, args.suf, url, args.db))
    p.close()
    p.join()
    print("-" * 30)
    print(f"Total time used: {(time.time() - start):.2f}s")
    print("-" * 30)
