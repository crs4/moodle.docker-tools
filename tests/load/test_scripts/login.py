import random
from common import BaseTransaction


class Transaction(BaseTransaction):
    def transaction_name(self):
        return "Login"

    def transaction_flow(self, timer_registry):
        browser = self._make_browser()
        resp = BaseTransaction.go_to_page(timer_registry, browser, "",
                                          timer_name="HomePage", sleep_time=1)
        resp = BaseTransaction.go_to_page(timer_registry, browser, "login/index.php",
                                          timer_name="LoginPage",
                                          sleep_time=1)

        login_form = self._get_form(browser, "login")
        assert (login_form), "Error: unable to find the LOGIN form"

        login_form.set_all_readonly(False)

        user = random.choice(self.get_list_of_users())
        assert (user), "Error: unable to find a valid user"

        login_form["username"] = user["username"]
        login_form["password"] = user["password"]

        browser.submit()

        return browser


if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
