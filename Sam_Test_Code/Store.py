__author__ = 'ywu'
import re

class SuperCash(object):
    @staticmethod
    def cash_accept(self, money):
        return money


class SuperCashNormal(SuperCash):

    def cash_accept(self, money):
        return money


class SuperCashDiscount(SuperCash):

    def __init__(self, discount):
        self.discount = float(discount)

    def cash_accept(self,money):
        return money*self.discount


class SuperCashReturn(SuperCash):

    def __init__(self, money_condition, money_return):
        self.money_condition = money_condition
        self.money_return = money_return
        if self.money_condition <= self.money_return:
            print "money return should not large than money condition!!!"
            raise BaseException

    def cash_accept(self, money):
        _result = 0
        try:
            _result = money//self.money_condition*self.money_return
        except ZeroDivisionError:
            print "money condition should not be zero!!!"
        return money - _result


class CashContext(object):

    def __init__(self, cash_type=None):
        if cash_type == None:
            cash_type =[]
        self.cash_type = cash_type
        self.cs = None

    def getresult(self, money):
        _total = money
        cash_number = len(self.cash_type)
        if cash_number == 0:
            self.cs = SuperCashNormal()
            _total = self.cs.cash_accept(money)
        if cash_number != 0:
            for i in range(0, cash_number):
                R = re.compile(r"\d+/+\d+")
                cash_flag = re.match(R, self.cash_type[i])
                if cash_flag:
                    money_condition = float(self.cash_type[i].split("/")[0])
                    money_return = float(self.cash_type[i].split("/")[1])
                    self.cs = SuperCashReturn(money_condition, money_return)
                    _total = self.cs.cash_accept(_total)
                else:
                    self.cs = SuperCashDiscount(self.cash_type[i])
                    _total = self.cs.cash_accept(_total)

        return _total


if __name__ == "__main__":
    discount = CashContext(["0/20"])
    total = discount.getresult(2000.00)
    print total










