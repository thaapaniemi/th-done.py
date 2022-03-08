#!/usr/bin/python3
"""
    v.0.1 Initial release
"""

import argparse
import os
import sqlite3
import decimal
import datetime
import time

parser = argparse.ArgumentParser(description='Simple DONE tracking tool')
parser.add_argument('query', nargs="*")


class DoneDB(object):
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

    def list(self, status=None):
        items = []

        delta = datetime.timedelta(weeks=1)

        q = 'SELECT item_id, description, timestamp FROM items  WHERE timestamp > ? ORDER BY timestamp'
        args = [delta.total_seconds()]

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


def main(args, config):

    with DoneDB(config["database"]) as done:
        if args.query:
            description = " ".join(args.query)
            done.add(description)
            print("added.")
            return

        prev_date_time = None
        for item in done.list():
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
