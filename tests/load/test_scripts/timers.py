import os
import MySQLdb
import socket
import time
import datetime


class TimerRegistry(object):
    def __init__(self, transaction):
        self._transaction = transaction
        self._raw_timers = []
        self._transaction_name = str(time.time()) + "@" + socket.gethostname()

    def add_timer(self, timer_name, start_time, latency, response_code=0):
        self._transaction.custom_timers[timer_name] = latency
        tc_name = "CODE_" + str(response_code)
        if not self._transaction.custom_timers.has_key(tc_name):
            self._transaction.custom_timers[tc_name] = 0
        self._transaction.custom_timers[tc_name] += 1
        self._raw_timers.append((timer_name, start_time, latency, response_code))

    def write_timers_to_db(self):
        host = os.environ["MYSQL_HOST"]
        user = os.environ["MYSQL_USER"]
        passwd = os.environ["MYSQL_PASSWORD"]
        db = os.environ["LOAD_TEST_DB"]
        conn = MySQLdb.connect(host, user, passwd, db)
        x = conn.cursor()
        try:
            for timer in self._raw_timers:
                # timer fields: timer_name, timestamp, latency, http_code
                timestamp = datetime.datetime.fromtimestamp(timer[1]).isoformat()
                x.execute(
                    """INSERT INTO result(transaction,request,start_time,latency,http_code) VALUES (%s,%s,%s,%s,%s)""",
                    (self._transaction_name, timer[0], timestamp, timer[2], timer[3]))
            conn.commit()
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
            conn.rollback()
            return False
        conn.close()
        return True
