import re
import time
import users
import statsd
import random
import logging
from settings import configuration
from questions import get_questions, QUESTION_IMAGE_NAVIGATION_LOAD
from locust import task, events, web, HttpLocust, TaskSet, InterruptTaskSet


class BaseTaskSet(TaskSet):
    def __init__(self, parent):
        super(BaseTaskSet, self).__init__(parent)
        self._stats = statsd.StatsClient(configuration["statsd"]["server_address"],
                                         configuration["statsd"]["server_port"])
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)

        # setting the hostname
        if isinstance(parent, HttpLocust) or hasattr(parent, "host"):
            self._logger.debug("Locust HOST: %s", parent.host)
            self.host = parent.host


class Login(BaseTaskSet):
    def __init__(self, parent):
        super(Login, self).__init__(parent)
        self._users = users.get_users()

    def on_start(self):
        self._logger.debug("Starting %s", __name__)
        self.client.verify = False

    @property
    def users(self):
        return self._users

    @task(1)
    def index(self):
        with self._stats.timer('moodle.home'):
            self.client.get("/")

    @task(1)
    def login_page(self):
        with self._stats.timer('moodle.login.index'):
            self.client.get("/login/index.php")

    @task(1)
    def login(self, logout=True):
        user = random.choice(self.users)
        self._logger.debug("Trying to log %r", user.username)
        with self._stats.timer('moodle.login.submit'), \
             self.client.post("/login/index.php", {
                 'username': user.username,
                 'password': user.password
             }, name="/login/index.php [username] [password]", catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")
                raise InterruptTaskSet("Login failed for user %s" % user.username)
            else:
                self._logger.debug("Log in succeded: %r", user)
                # self._stats.set('moodle.users.set', user.username)
                self._stats.gauge('moodle.users.count', 1, delta=True)
                m = re.search('sesskey=(\S+)', response.content)
                session_key = m.group(1) if m else None
                if not session_key:
                    raise InterruptTaskSet("Unable to find the session key for the user %s" % user.username)
                user.sessionkey = session_key
                self._logger.debug("User sessionKey: %s", user.sessionkey)
        if logout:
            with self._stats.timer('moodle.logout.submit'):
                self.logout(user)

        return (user)

    def logout(self, user):
        if not user or not user.sessionkey:
            raise ValueError("Invalid session key")
        with self._stats.timer('moodle.logut.submit'), \
             self.client.get("/login/logout.php?sessKey=%s" % user.sessionkey,
                             name="/logout.php?sessKey=[id]",
                             catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")
                raise InterruptTaskSet("Logout failed for user %s (sessionKey: %s)" % (user.username, user.sessionkey))
            else:
                self._logger.debug("Logout succeded")
                self._stats.gauge('moodle.users.count', -1, delta=True)


class NavigateImage(BaseTaskSet):
    def __init__(self, parent):
        super(NavigateImage, self).__init__(parent)
        # preload questions
        self._questions = get_questions()

    def on_start(self):
        self._login_task = Login(self)
        self._logger.debug("Starting %s", __name__)
        self.client.verify = False

    @property
    def questions(self):
        return self._questions

    @task
    def navigate_image(self):
        # go to home
        self._login_task.index()
        # go to login page
        self._login_task.login_page()
        # perform login
        user = self._login_task.login(logout=False)
        self._logger.debug("The current user %r", user)

        w = random.randint(0, 10)
        time.sleep(w)

        # select a question
        question = random.choice(self.questions)
        # question = self.questions.pop()
        self._logger.debug("Selected question: %r", question)
        question.load(browser=self.client, host=self.host)
        self._logger.debug("Loaded question %r", question)
        self._logger.debug("Loaded question info %r", question._info)

        question.navigate_image(QUESTION_IMAGE_NAVIGATION_LOAD.HIGH,
                                multithread=False, think_time_per_level=0)
        # perform logout
        self._login_task.logout(user)


class MyLocust(HttpLocust):
    # reset gauges
    stats = statsd.StatsClient(configuration["statsd"]["server_address"], configuration["statsd"]["server_port"])
    stats.gauge('moodle.users.count', 0)
    task_set = NavigateImage
    min_wait = 1000
    max_wait = 5000


"""
We need somewhere to store the stats.
On the master node stats will contain the aggregated sum of all content-lengths,
while on the slave nodes this will be the sum of the content-lengths since the
last stats report was sent to the master
"""
stats = {"content-length": 0}


def on_request_success(request_type, name, response_time, response_length):
    """
    Event handler that get triggered on every successful request
    """
    print "%s: %s -- %s, %s" % (name, request_type, response_time, response_length)
    stats["content-length"] += response_length


def on_report_to_master(client_id, data):
    """
    This event is triggered on the slave instances every time a stats report is
    to be sent to the locust master. It will allow us to add our extra content-length
    data to the dict that is being sent, and then we clear the local stats in the slave.
    """
    data["content-length"] = stats["content-length"]
    stats["content-length"] = 0


def on_slave_report(client_id, data):
    """
    This event is triggered on the master instance when a new stats report arrives
    from a slave. Here we just add the content-length to the master's aggregated
    stats dict.
    """
    stats["content-length"] += data["content-length"]


def on_locust_error(locust_instance, exception, tb):
    print "%r" % locust_instance
    print "%r" % exception
    print "%r" % tb


def on_hatch_completed(user_count):
    print "Hatch completed: %r" % user_count


def on_quitting():
    print "Quitting"


# Hook up the event listeners
events.request_success += on_request_success
events.report_to_master += on_report_to_master
events.slave_report += on_slave_report
events.locust_error += on_locust_error
events.hatch_complete += on_hatch_completed
events.quitting += on_quitting


@web.app.route("/content-length")
def total_content_length():
    """
    Add a route to the Locust web app, where we can see the total content-length
    """
    return "Total content-length recieved: %i" % stats["content-length"]
