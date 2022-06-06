import pytest

import palm as pm

@pytest.fixture
def initial_deposit():
    return 10000

@pytest.fixture
def account(initial_deposit):
    return pm.CashAccount(initial_deposit=initial_deposit)

def test_SufficientFunds_WithdrawalApproved(account, initial_deposit):
    allowed_amount = 10.0
    response = account.submit_withdrawal_request(allowed_amount)
    assert response.result == pm.WithdrawalResult.APPROVED
    assert response.reason == None
    assert (
        abs(account.balance - (initial_deposit - allowed_amount)) < 1.0e-5
    )  ## This is dumb and hard coded but should be fine.

def test_InsufficientFunds_WithdrawalDeclined(account, initial_deposit):

    ## Test declining from insufficient funds
    requested_amount = initial_deposit + 10.0
    response = account.submit_withdrawal_request(requested_amount)

    assert response.result == pm.WithdrawalResult.DECLINED
    assert response.reason == pm.WithdrawalResponse.DeclinedReason.INSUFFICIENT_FUNDS
    assert abs(account.balance - initial_deposit) < 1.0e-5

def test_NegativeWithdrawalAmount_WithDrawalDeclined(account, initial_deposit):
    ## try and withdraw a negative amount
    requested_amount = -1.0
    response = account.submit_withdrawal_request(requested_amount)
    assert response.result == pm.WithdrawalResult.DECLINED
    assert (
        response.reason == pm.WithdrawalResponse.DeclinedReason.NEGATIVE_AMOUNT_REQUESTED
    )
    assert abs(account.balance - initial_deposit) < 1.0e-5

def test_PositiveDeposit_DepositApproved(account, initial_deposit):

    amount = 10.0
    response = account.submit_deposit_request(amount)
    assert response.result == pm.DepositResult.CONFIRMED
    assert response.reason == None
    assert abs(account.balance - (initial_deposit + amount)) < 1.0e-5

def test_NegativeDeposit_DepositDeclined(account, initial_deposit):

    response = account.submit_deposit_request(-1.0)
    assert response.result == pm.DepositResult.DECLINED
    assert response.reason == pm.DepositResponse.DeclinedReason.NEGATIVE_AMOUNT_DEPOSITED
