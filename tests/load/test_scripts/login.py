from common import BaseTransaction


class Transaction(BaseTransaction):

    def transaction_name(self):
        return "Login"

    def transaction_flow(self):
        browser = self._make_browser()
        resp = self._go_to_page(browser, "", timer_name="HomePage", sleep_time=1)
        resp = self._go_to_page(browser, "login/index.php", timer_name="LoginPage", sleep_time=1)

        login_form = self._get_form(browser, "login")
        assert(login_form), "Error: unable to find the LOGIN form"

        login_form.set_all_readonly(False)

        login_form["username"] = "admin"
        login_form["password"] = "!#Moodle2016"

        browser.submit()

        return browser


if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers