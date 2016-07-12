#!/usr/bin/env python
import os
import csv
import MySQLdb


def load_from_file(filename="users.csv"):
    result = []
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter="\t")
        for row in spamreader:
            result.append(row[0], row[1])
    return result


def load_form_db(
        host=os.environ["MYSQL_HOST"],
        user=os.environ["MYSQL_USER"],
        passwd=os.environ["MYSQL_PASSWORD"],
        db=os.environ["MYSQL_DATABASE"]):
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    cur = db.cursor()
    cur.execute("SELECT username, password FROM mdl_user")
    result = []
    for row in cur.fetchall():
        result.append((row[0], row[1]))
    return result
