from question import Question
from login import Transaction as LoginTransaction


class Transaction(LoginTransaction):
    def transaction_name(self):
        return "Answer a question"

    def transaction_flow(self, timer_registry):
        browser = super(Transaction, self).transaction_flow(timer_registry)

        # Question Bank link
        qbank_link = browser.find_link(text="Question bank")
        resp = browser.follow_link(qbank_link)

        # simulate the selection of the question
        # ---> select a proper question category from the QuestionBank ????
        # OR use a pre-loaded set of category to switch to the category page

        # active the preview of a given question
        question = Question(browser, 566, timer_registry=timer_registry)

        # self._question = question
        self._question = question

        question.navigate_image(0, multithread=True)

        return browser


if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
