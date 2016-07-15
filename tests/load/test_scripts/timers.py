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


def report_timers(timer_registry, timer_name, start_time, latency, response=0):
    print "Print timer before...."
    print timer_registry

    if TIMER_TYPE == "analytic":
        report_analytic_timers(timer_registry, timer_name, start_time, latency, response)
    else:
        report_average_timers(timer_registry, timer_name, start_time, latency, response)
    print "Print timer after...."
    print timer_registry

    append_timer(timer_registry, timer_name, start_time, latency, response)


def report_analytic_timers(timer_registry, timer_name, start_time, latency, response = 0):
    if timer_registry.has_key(timer_name):
        timer_registry[timer_name] = []
    timer_registry[timer_name].append(latency)
    if isinstance(response, int):
        response_code = response
    else:
        response_code = response.status_code if hasattr(response, "status_code") else response.code
    print response_code
    if response_code in HTTP_CODES:
        tc_name = "CODE_" + str(response_code)
        if not timer_registry.has_key(tc_name):
            timer_registry[tc_name] = []
        timer_registry[tc_name].append(1)
    for code in HTTP_CODES:
        if code != response_code:
            tc_name = "CODE_" + str(code)
            if not timer_registry.has_key(tc_name):
                timer_registry["CODE_" + str(tc_name)] = []
            timer_registry["CODE_" + str(tc_name)].append(0)


def report_average_timers(timer_registry, timer_name, start_time, latency, response=0):
    timer_registry[timer_name] = latency
    if isinstance(response, int):
        response_code = response
    else:
        response_code = response.status_code if hasattr(response, "status_code") else response.code
    print response_code
    if response_code in HTTP_CODES:
        tc_name = "CODE_" + str(response_code)
        if timer_registry.has_key(tc_name):
            timer_registry[tc_name] += 1
        else:
            timer_registry[tc_name] = 1
    for code in HTTP_CODES:
        if code != response_code:
            tc_name = "CODE_" + str(code)
            if not timer_registry.has_key(tc_name):
                timer_registry["CODE_" + str(tc_name)] = 0
