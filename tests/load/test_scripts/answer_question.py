from login import Transaction as LoginTransaction
from common import BaseTransaction


class Transaction(LoginTransaction):

    def transaction_name(self):
        return "Answer a question"

    def transaction_flow(self):
        browser = super(Transaction, self).transaction_flow()

        return browser


if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
