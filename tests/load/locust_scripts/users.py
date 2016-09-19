#!/usr/bin/env python
import csv
import logging
import os
import random
import socket
import string
import MySQLdb
import settings

# module logger
logger = logging.getLogger(__name__)

# preloaded list of users
_USER_LIST = None

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

    def __str__(self):
        return "%s (%s %s)" % (self.username, self.firstname, self.lastname)

    def __repr__(self):
        return self.__str__()


def get_users(force_reload=False):
    if not _USER_LIST or force_reload:
        filename = settings.USERS_FILENAME
        if not os.path.isfile(filename):
            base_path = os.path.dirname(__file__)
            path = (base_path + "/../../") if base_path else '../../'
            filename = path + filename
            if not os.path.isfile(filename):
                raise Exception("User list not found")
        return load_from_file(filename)
    return _USER_LIST


def load_from_file(filename=settings.USERS_FILENAME, delimiter=',', as_dict=False):
    result = []
    with open(filename, 'rb') as csvfile:
        logger.info("Reading users from file '%s'...", filename)
        if as_dict:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for user in reader:
                result.append(user)
        else:
            spamreader = csv.reader(csvfile, delimiter=delimiter)
            header = True
            for (username, password, firstname, lastname, email, cohort1) in spamreader:
                if not header:
                    result.append(User(username, password, firstname, lastname, email, cohort1))
                else:
                    header = False
    return result


def load_from_db(host, user, passwd, db):
    host = os.environ["MYSQL_HOST"] if not host else host
    user = os.environ["MYSQL_USER"] if not user else user
    passwd = os.environ["MYSQL_PASSWORD"] if not passwd else passwd
    db = os.environ["MYSQL_DATABASE"] if not db else db
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    cur = db.cursor()
    cur.execute("SELECT username, password FROM mdl_user")
    result = []
    for row in cur.fetchall():
        result.append((row[0], row[1]))
    return result


def generate_users(num_of_users=1,
                   user_prefix=settings.USER_PREFIX, user_cohort=settings.USER_COHORT, as_dict=False):
    result = []
    if type(num_of_users) != int:
        raise ValueError("'num_of_users' must be an integer")
    hostname = socket.gethostname()
    for i in range(0, num_of_users):
        username = ''.join([user_prefix, str(i)])
        if as_dict:
            result.append({
                'username': username,
                'password': _generate_password(False),
                'firstname': ''.join(["FN", str(i)]),
                'lastname': ''.join(["LN", str(i)]),
                'email': '@'.join([username, hostname]),
                'cohort1': user_cohort
            })
        else:
            result.append(User(
                username, _generate_password(False),
                firstname=''.join(["FN", str(i)]),
                lastname=''.join(["LN", str(i)]),
                email='@'.join([username, hostname]),
                cohort1=user_cohort
            ))
    return result


def write_users(users, filename=settings.USERS_FILENAME):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=USER_PROPERTIES)
        writer.writeheader()
        for user in users:
            writer.writerow(user)


def _generate_password(random_choice=True):
    if random_choice:
        length = 13
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        random.seed = (os.urandom(1024))
        return ''.join(random.choice(chars) for i in range(length))
    else:
        return "testUser@M2!"


# preload a list of users
_USER_LIST = get_users()
