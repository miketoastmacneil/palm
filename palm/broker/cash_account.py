
import pprint

class  CashAccount:

    def __init__(self, initial_deposit):

        self.balance = initial_deposit

    def withdraw(self, amount):

        self.balance = self.balance - amount

    def deposit(self, amount):
        
        self.balance = self.balance +  amount

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Account Balance: " : self.balance
        }
        return pp.pformat(state)