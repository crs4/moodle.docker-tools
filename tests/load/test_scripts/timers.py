import os, MySQLdb
import datetime, time
from settings import HTTP_CODES, TIMER_TYPE


def append_timer(timer_registry, timer_name, start_time, latency, response):
    host = os.environ["MYSQL_HOST"]
    user = os.environ["MYSQL_USER"]
    passwd = os.environ["MYSQL_PASSWORD"]
    db = os.environ["LOAD_TEST_DB"]
    if isinstance(response, int):
        http_code = response
    else:
        http_code = response.status_code if hasattr(response, "status_code") else response.code
    conn = MySQLdb.connect(host, user, passwd, db)
    x = conn.cursor()
    try:
        timestamp = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        x.execute("""INSERT INTO result(request,start_time,latency,http_code) VALUES (%s,%s,%s,%s)""",
                  (timer_name, timestamp, latency, http_code))
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
        response_code = response.status_code if hasattr(response, "status_code") else response.code
        if response_code in HTTP_CODES:
            timer_registry["CODE_" + str(response_code)] = 1
        for code in HTTP_CODES:
            if code != response_code:
                timer_registry["CODE_" + str(code)] = 0
