#!/usr/bin/python3
"""
    v.0.1 Initial release
    v.0.2 Fix date limit
"""

import argparse
import os
import sqlite3
import decimal
import datetime
import time

parser = argparse.ArgumentParser(description='Simple DONE tracking tool')
parser.add_argument('query', nargs="*")
parser.add_argument('-all', action='store_true', help='Print all items')


class DoneDB(object):
    """docstring for DoneDB"""
    dbpath = None
    con = None

    def __init__(self, dbpath):
        super(DoneDB, self).__init__()
        self.dbpath = dbpath
        self.init_database()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.close()

    def init_database(self):
        self.con = sqlite3.connect(self.dbpath)

        cur = self.con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS items
        (
            item_id     INTEGER PRIMARY KEY,
            description TEXT,
            timestamp   BIGINT
        );""")

        self.con.commit()

    def list(self, status=None, print_all=False):
        items = []

        delta = datetime.timedelta(weeks=1)

        start_time = time.time() - delta.total_seconds()

        q = 'SELECT item_id, description, timestamp FROM items  WHERE timestamp > ? ORDER BY timestamp'

        if print_all:
            start_time = 0

        args = [start_time]

        cur = self.con.cursor()
        for row in cur.execute(q, args):
            items.append({
                "item_id": row[0],
                "description": row[1],
                "timestamp": row[2],
            })

        return items

    def add(self, description):

        now = datetime.datetime.now()

        cur = self.con.cursor()
        cur.execute("""INSERT INTO items (description, timestamp) VALUES (?, ?);""", (description, time.mktime(now.timetuple())))
        self.con.commit()

    def delete(self, item_id):
        cur = self.con.cursor()
        cur.execute("""DELETE FROM items WHERE item_id=?;""", (item_id, ))
        self.con.commit()

    def update_status(self, item_id, status):
        cur = self.con.cursor()
        cur.execute("""UPDATE items SET status=? WHERE item_id=?;""", (
            status,
            item_id,
        ))
        self.con.commit()

    def update_used_time(self, item_id, used_time):
        cur = self.con.cursor()

        cur.execute("""UPDATE items SET used_time=used_time+? WHERE item_id=?;""", (
            str(used_time),
            item_id,
        ))
        self.con.commit()


def main(args, config):

    with DoneDB(config["database"]) as done:
        if args.query:
            description = " ".join(args.query)
            done.add(description)
            print("added.")
            return

        prev_date_time = None
        for item in done.list(print_all=args.all):
            date_time = datetime.datetime.fromtimestamp(item["timestamp"])
            date_str = date_time.strftime('%Y-%m-%d %H:%M:%S')

            if prev_date_time and prev_date_time.day != date_time.day:
                print(" ")

            print("[{timestamp:5}] {description}".format(timestamp=date_str, description=item["description"]))
            prev_date_time = date_time


if __name__ == '__main__':

    config = {"database": os.path.join(os.path.expanduser('~'), ".done.sqlite")}

    args = parser.parse_args()
    main(args, config)
