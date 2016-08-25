#!/usr/bin/env python
import os
import csv
import random
import string
import socket
import MySQLdb

# default filename containing test users
USERS_FILENAME = 'users.csv'
# default user prefix
USER_PREFIX = 'testuser'
# default user cohort
USER_COHORT = 'test_users'

# list of user properties
USER_PROPERTIES = ['username', 'password', 'firstname', 'lastname', 'email', 'cohort1']


class User:
    def __init__(self, username, password, firstname, lastname, email, cohort1):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.cohort1 = cohort1


def get_users():
    users = []
    filename = USERS_FILENAME
    if not os.path.isfile(filename):
        base_path = os.path.dirname(__file__)
        path = (base_path + "/../../") if base_path else '../../'
        filename = path + filename
        if not os.path.isfile(filename):
            raise Exception("User list not found")
        users = load_from_file(filename)
    return users


def load_from_file(filename=USERS_FILENAME, delimiter=',', skip_header=True, as_dict=False):
    result = []
    with open(filename, 'rb') as csvfile:
        if as_dict:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for user in reader:
                result.append(user)
        else:
            spamreader = csv.reader(csvfile, delimiter=delimiter)
            for (username, password, firstname, lastname, email, cohort1) in spamreader:
                result.append(User(username, password, firstname, lastname, email, cohort1))
    return result


def load_from_db(
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


def generate_users(num_of_users=1, user_prefix=USER_PREFIX, user_cohort=USER_COHORT, as_dict=False):
    result = []
    if type(num_of_users) != int:
        raise ValueError("'num_of_users' must be an integer")
    hostname = socket.gethostname()
    for i in range(0, num_of_users):
        username = ''.join([user_prefix, str(i)])
        if as_dict:
            result.append({
                'username': username,
                'password': _generate_password(),
                'firstname': ''.join(["FN", str(i)]),
                'lastname': ''.join(["LN", str(i)]),
                'email': '@'.join([username, hostname]),
                'cohort1': user_cohort
            })
        else:
            result.append(User(
                username, _generate_password(),
                firstname=''.join(["FN", str(i)]),
                lastname=''.join(["LN", str(i)]),
                email='@'.join([username, hostname]),
                cohort1=user_cohort
            ))
    return result


def write_users(users, filename=USERS_FILENAME):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=USER_PROPERTIES)
        writer.writeheader()
        for user in users:
            writer.writerow(user)


def _generate_password():
    length = 13
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))
