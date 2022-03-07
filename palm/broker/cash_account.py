from enum import Enum
import pprint


class WithdrawalResult(Enum):
    APPROVED = 1
    DECLINED = 2


class DepositResult(Enum):
    CONFIRMED = 1
    DECLINED = 2


class WithdrawalResponse:
    class DeclinedReason(Enum):
        INSUFFICIENT_FUNDS = 1
        NEGATIVE_AMOUNT_REQUESTED = 1

    def __init__(self, result: WithdrawalResult, reason: DeclinedReason = None):
        self.result = result
        self.reason = reason


class DepositResponse:
    class DeclinedReason(Enum):
        NEGATIVE_AMOUNT_DEPOSITED = 1

    def __init__(self, result: DepositResult, reason=None):
        self.result = result
        self.reason = reason


class Transaction(Enum):
    WITHDRAWAL = 1
    DEPOSIT = 2


class TransactionRecord:
    def __init__(
        self, transaction_type, transaction_response, previous_balance, current_balance
    ):
        self.transaction_type = transaction_type
        self.transaction_response = transaction_response
        self.previous_balance = previous_balance
        self.current_balance = current_balance

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4)
        state = {
            "Transaction Type: ": self.transaction_type,
            "Transaction Result: ": self.transaction_response.result,
            "Previous Balance: ": self.previous_balance,
            "Current Balance: ": self.current_balance,
        }
        return pp.pformat(state)


class CashAccount:
    def __init__(self, initial_deposit):

        self._transaction_history = [
            TransactionRecord(
                Transaction.DEPOSIT,
                DepositResponse(DepositResult.CONFIRMED),
                0.0,
                initial_deposit,
            )
        ]

    def submit_withdrawal_request(self, amount):

        if amount < 0:
            return self._handle_negative_withdrawal_request()
        if amount > self.balance:
            return self._handle_insufficient_funds_withdrawal_request()
        else:
            return self._handle_approved_withdrawal(amount)

    def submit_deposit_request(self, amount):

        if amount < 0:
            return self._handle_negative_deposit_request()
        else:
            return self._handle_successful_deposit_request(amount)

    @property
    def history(self):
        return self._transaction_history

    def _handle_negative_withdrawal_request(self):
        response = WithdrawalResponse(
            WithdrawalResult.DECLINED,
            WithdrawalResponse.DeclinedReason.NEGATIVE_AMOUNT_REQUESTED,
        )
        previous_balance = self.balance
        new_balance = previous_balance
        record = TransactionRecord(
            Transaction.WITHDRAWAL, response, previous_balance, new_balance
        )
        self._transaction_history.append(record)

        return response

    def _handle_insufficient_funds_withdrawal_request(self):
        response = WithdrawalResponse(
            WithdrawalResult.DECLINED,
            WithdrawalResponse.DeclinedReason.INSUFFICIENT_FUNDS,
        )
        previous_balance = self.balance
        new_balance = previous_balance
        record = TransactionRecord(
            Transaction.WITHDRAWAL, response, previous_balance, new_balance
        )
        self._transaction_history.append(record)
        return response

    def _handle_approved_withdrawal(self, amount):
        response = WithdrawalResponse(WithdrawalResult.APPROVED)
        previous_balance = self.balance
        new_balance = previous_balance - amount
        record = TransactionRecord(
            Transaction.WITHDRAWAL, response, previous_balance, new_balance
        )
        self._transaction_history.append(record)
        return response

    def _handle_negative_deposit_request(self):
        response = DepositResponse(
            DepositResult.DECLINED,
            DepositResponse.DeclinedReason.NEGATIVE_AMOUNT_DEPOSITED,
        )
        previous_balance = self.balance
        new_balance = previous_balance
        record = TransactionRecord(
            Transaction.DEPOSIT, response, previous_balance, new_balance
        )
        self._transaction_history.append(record)
        return response

    def _handle_successful_deposit_request(self, amount):
        response = DepositResponse(DepositResult.CONFIRMED)
        previous_balance = self.balance
        new_balance = previous_balance + amount
        record = TransactionRecord(
            Transaction.DEPOSIT, response, previous_balance, new_balance
        )
        self._transaction_history.append(record)
        return response

    @property
    def balance(self):
        return self._transaction_history[-1].current_balance

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4)
        state = {"Account Balance: ": self.balance}
        return pp.pformat(state)
