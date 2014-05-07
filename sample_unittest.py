#!/usr/bin/python

import unittest

class Case1(unittest.TestCase):
    def setUp(self):
        print("setup")
    
    def tearDown(self):
        print("teardown")
        
    def test11(self):
        print("test11")
        self.assertEqual(1, 1)

    def test12(self):
        print("test12")
        self.assertEqual(1, 2)

class Case2(unittest.TestCase):
    def test21(self):
        print("test21")
        self.assertEqual(1, 2, "test faild 1 != 2")
        
    def test22(self):
        raise Exception("exception")

result = unittest.TestResult()

suite = unittest.TestSuite()
suite.addTest(Case1("test11"))
suite.addTest(Case1("test12"))
suite.addTest(Case2("test21"))
suite.addTest(Case2("test22"))
suite.run(result)

#result = unittest.TextTestRunner(verbosity=2).run(suite)
for error in result.errors:
    case = error[0]
    errmsg = error[1]
    print("error cases: ", case, errmsg)
for failure in result.failures:
    case = failure[0]
    failmsg = failure[1]
    print("fail cases: ", case, failmsg)
