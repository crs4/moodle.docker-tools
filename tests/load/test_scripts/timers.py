HTTP_CODES = [200, 300, 301, 302, 303, 304, 400, 401, 403, 404, 405, 406, 408, 500]


def report_timers(timer_registry, timer_name, response, latency):
    if timer_registry is not None:
        if timer_registry:
            timer_registry[timer_name] = latency
        response_code = response.status_code if hasattr(response, "status_code") else response.code
        if response_code in HTTP_CODES:
            timer_registry["CODE_" + str(response_code)] = 1
        for code in HTTP_CODES:
            if code != response_code:
                timer_registry["CODE_" + str(code)] = 0
