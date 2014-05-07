
class Operation(object):
    @staticmethod
    def number_a(self):
        A = raw_input("Please inout number A:")
        return float(A)
    @staticmethod
    def number_b(self):
        B = raw_input("Please input number B")
        return float(B)

    def getresult(self):
        result = 0
        return result


class Operation_Add(Operation):
    @staticmethod
    def getresult(self):
        result = 0
        result = self.number_a(self) + self.number_b(self)
        return result


class Operation_Sub(Operation):
    @staticmethod
    def getresult(self):
        result = 0
        result = self.number_a(self) - self.number_b(self)
        return result


class Operation_Mul(Operation):
    @staticmethod
    def getresult(self):
        result = 0
        result = self.number_a(self) * self.number_b(self)
        return result


class Operation_Div(Operation):
    @staticmethod
    def getresult(self):
        result = 0
        try:
            result = self.number_a(self) /self.number_b(self)
        except ZeroDivisionError:
            print "Number B can not be Zero"
        return result


if __name__ == "__main__":

    Input_operation = raw_input("Please input what operation you want to do (Add/Sub/Mul/Div):")
    Calculator = eval("Operation_" + Input_operation + ".getresult(Operation)")
    print Calculator

