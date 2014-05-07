#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os

try:
    from xmlrpclib import ServerProxy
except ImportError:
    from xmlrpc.client import ServerProxy


class TestLinkAdapterError(Exception):
    pass


class TestProject(object):
    def __init__(self, srvProxy, devKey, data): 
        self.server = srvProxy
        self.devKey = devKey
        self.data = data
        self.__id = self.getId()
        self.__name = self.getName()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<TestProject '%s(ID:%s)'>" % (self.__name, self.__id)
        
    def getId(self):
        return int(self.data["id"])

    def getName(self):
        return self.data["name"]
    
    def createTestPlan(self, planname):
        params = {"devKey":self.devKey, "testplanname": planname, "testprojectname": self.__name}
        resp = self.server.tl.createTestPlan(params)
        """
        [{'message': 'Success!', 'id': '87129', 'status': True, 'operation': 'createTestPlan', 'additionalInfo': ''}]
        [{'code': 3034, 'message': '(createTestPlan) - Test Plan (name:TestXMLRPCAPI) Already EXITS on Test Project (name:test).'}]
        [{'code': 7011, 'message': '(createTestPlan) - Test Project (name:test12314) does not exist.'}]
        """
        logger.debug("Call TestLink API: createTestPlan(%s), Response: %s", params, resp)
        plan = None
        if "code" in resp[0]:
            if resp[0]["code"] == 3034:
                logger.error("TestPlan '%s' already exists on TestProject '%s(ID:%s)'", planname, self.__name, self.__id)
            elif resp[0]["code"] == 7011:
                logger.error("Fail to create TestPlan '%s' on TestProject '%s(ID:%s)'", planname, self.__name, self.__id)
            else:
                raise
        else:
            logger.debug("Create TestPlan '%s' on TestProject '%s(ID:%s)' Done", planname, self.__name, self.__id)
            plan = TestPlan(self.server, self.devKey, resp[0]["id"], planname, self.__id)
        return plan

    def getTestPlans(self):
        params = {"devKey":self.devKey, "testprojectid": self.__id}
        resp = self.server.tl.getProjectTestPlans(params)
        """
        [{'testproject_id': '14979', 'notes': '', 'is_public': '1', 'name': 'TestReport2TL', 'id': '87109', 'active': '1'}]
        [{'code': 7000, 'message': '(getProjectTestPlans) - The Test Project ID (11111) provided does not exist!'}]
        """
        logger.debug("Call TestLink API: getProjectTestPlans(%s), Response: %s", params, resp)  
        plans = []
        if not resp:
            logger.debug("No TestPlans on Project '%s(ID:%s)'", self.__name, self.__id)
        else:
            if "code" in resp[0]:
                logger.error("Can't find the TestPlans on Project '%s(ID:%s)'", self.__name, self.__id)
            else:
                for tlPlan in resp:
                    plans.append(TestPlan(self.server, self.devKey, tlPlan["id"], tlPlan["name"], self.__id))
        return plans

    def getTestPlanByName(self, planname):
        retPlan = None
        for plan in self.getTestPlans():
            if plan.getName() == planname:
                retPlan = plan
        return retPlan
    
    def createTopLevelTestSuite(self, suitename):
        details   = 'Create by %s in %s' % (os.getenv('USERNAME'), os.getenv('COMPUTERNAME'))
        params = {"devKey":self.devKey, "testprojectid": self.__id, "testsuitename": suitename, "details": details}
        resp = self.server.tl.createTestSuite(params)
        """
        [{'status': True, 'additionalInfo': '', 'name': '', 'name_changed': False, 'id': '87130', 'message': 'ok', 'operation': 'createTestSuite'}]
        {'name_changed': False, 'id': 0, 'status_ok': 0, 'msg': "There's already a Test Suite with name: TestXMLRPCAPI", 'name': ''}
        [{'message': '(createTestSuite) - The Test Project ID (1497911) provided does not exist!', 'code': 7000}]
        """
        logger.debug("Call TestLink API: createTestSuite(%s), Response: %s", params, resp)
        suite = None
        if isinstance(resp, list):
            if "code" in resp[0]:
                logger.error("Fail to create ToplevelTestSuite '%s' on TestProject '%s(ID:%s)'", suitename, self.__name, self.__id)
            else:
                logger.debug("Create ToplevelTestSuite '%s' on TestProject '%s(ID:%s)' Done", suitename, self.__name, self.__id)
                suite = TestSuite(self.server, self.devKey, resp[0]["id"], suitename, self.__id)
        elif isinstance(resp, dict):
            logger.error("ToplevelTestSuite '%s' already exists on TestProject '%s(ID:%s)'", suitename, self.__name, self.__id)
        else:
            raise
        return suite

    def getTopLevelTestSuiteByName(self, testsuitename):
        suite = None
        for topLevelSuite in self.getTopLevelTestSuites():
            if topLevelSuite.getName() == testsuitename:
                suite = topLevelSuite
        return suite

    def getTopLevelTestSuites(self):
        params = {"devKey": self.devKey,"testprojectid": self.__id}
        resp = self.server.tl.getFirstLevelTestSuitesForTestProject(params)
        """
        [
        {'parent_id': '14979', 'node_type_id': '2', 'node_order': '0', 'id': '87111', 'name': 'Reset Test Suite', 'node_table': 'testsuites'}, 
        {'parent_id': '14979', 'node_type_id': '2', 'node_order': '0', 'id': '87124', 'name': 'Manual Connection Test Suite', 'node_table': 'testsuites'}, 
        ]
        [{'code': 7000, 'message': '(getFirstLevelTestSuitesForTestProject) - The Test Project ID (1497911) provided does not exist!'}]
        """
        logger.debug("Call TestLink API: getFirstLevelTestSuitesForTestProject(%s), Response: %s", params, resp)
        suites = []
        if not resp:
            logger.error("No top level TestSuites on TestProject '%s(ID:%s)", self.__name, self.__id)
        else:
            if "code" in resp[0]:
                logger.error("Get top level TestSuite on TestProject '%s(ID:%s)' Fail", self.__name, self.__id)
            else:
                for tlSuite in resp:
                    suites.append(TestSuite(self.server, self.devKey, tlSuite["id"], tlSuite["name"], self.__id))
        return suites

    def __TODO_getListedTestSuites(self):
        pass

    def getNestedTestSuites(self):
        """return data sample: 
        [
         {"suite": TestSuiteObject, "subsuites":[{"suite":TestSuiteObject, subsuites=[...]}, 
                                                 {"suite": TestSuiteObject, "subsuites":[] },
                                                ]
         {"suite": TestSuiteObject, "subsuites":[] }, 
        ]
        """
        def getSuites(suite):
            item = {}
            item["suite"] = suite
            item["subsuites"] = []
            for subSuite in suite.getSubTestSuites():
                item["subsuites"].append( getSuites(subSuite) )
            return item
        
        suites = []
        for topLevelSuite in self.getTopLevelTestSuites():
            suites.append( getSuites(topLevelSuite) )
        logger.debug("Get all TestSuites on TestProject '%s(ID:%s)': %s", self.__name, self.__id, suites)
        return suites    

    def getTestSuitesByName(self, testsuitename):
        suites = []

        def filtSuites(collection):
            for item in collection:
                if item["suite"].getName() == testsuitename:
                    suites.append( item["suite"] )
                filtSuites(item["subsuites"])
        filtSuites(self.getNestedTestSuites())
        if len(suites) == 0:
            logger.error("Can't find TestSuite '%s' on TestProject '%s(ID:%s)'", testsuitename, self.__name, self.__id)
        return suites

    def getTestCasesByName(self, testcasename):
        params = {"devKey":self.devKey, "testcasename":testcasename, "testprojectname": self.__name}
        resp = self.server.tl.getTestCaseIDByName(params)
        """
        {'1': {'parent_id': '87111', 'id': '87112', 'tc_external_id': '1', 'tsuite_name': 'Reset Test Suite', 'name': 'Source Side Reset'}}
        [{'parent_id': '90497', 'tc_external_id': '358', 'id': '90534', 'tsuite_name': 'Multi-channel LR Test Suite', 'name': 'Multichannel Test_HR=3, LR=3, Src=Coord, Sink=Station'}]
        [{'message': '(getTestCaseIDByName) - Cannot find matching test case. No testcase exists with the name provided!', 'code': 5030}]
        """
        logger.debug("Call TestLink API: getTestCaseIDByName(%s), Response: %s", params, resp)
        cases = []
        if isinstance(resp, dict):
            for tlCase in list(resp.values()):
                cases.append( TestCase(self.server, self.devKey, tlCase["id"], tlCase["name"]) )
        elif isinstance(resp, list):
            if "code" in resp[0]:
                logger.error("Can't find TestCase '%s' on TestProject '%s(ID:%s)'", testcasename, self.__name, self.__id)
            else:
                for tlCase in resp:
                    cases.append( TestCase(self.server, self.devKey, tlCase["id"], tlCase["name"]) )
        else:
            logger.error("Can't find TestCase '%s' on TestProject '%s(ID:%s)'", testcasename, self.__name, self.__id)
        return cases


class TestSuite(object):
    def __init__(self, srvProxy, devKey, suiteid, suitename, projectid):
        self.server = srvProxy
        self.devKey = devKey
        self.__id = suiteid
        self.__name = suitename
        self.__projectid = projectid
        self.__data = {}
    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<TestSuite '%s(ID:%s)'>" % (self.__name, self.__id)
    
    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def __getValue(self, key):
        if not self.__data:
            params = {"devKey":self.devKey,"testsuiteid": self.__id}
            resp = self.server.tl.getTestSuiteByID(params)
            """
            {'node_type_id': '2', 'parent_id': '14979', 'id': '87111', 'details': 'Create by yyang3 in SH-EA05446626', 'name': 'Reset Test Suite', 'node_order': '0'}
            [{'message': '(getTestSuiteByID) - ID 8711111 do not belongs to a Test Suite present on system!', 'code': 8000}]
            """
            logger.debug("Call TestLink API: getTestSuiteByID(%s), Response: %s", params, resp)
            if isinstance(resp, dict):
                self.__data = resp
            else:
                logger.error("Get TestSuite 'ID:%s' Fail", self.__id, self.__name)
        return self.__data[key]

    def createSubTestSuite(self, suitename):
        details = 'Create by %s in %s' % (os.getenv('USERNAME'), os.getenv('COMPUTERNAME'))
        params = {"devKey":self.devKey, "testprojectid": self.__projectid, "testsuitename": suitename, "details": details, "parentid": self.__id}
        resp = self.server.tl.createTestSuite(params)
        logger.debug("Call TestLink API: createTestSuite(%s), Response: %s", params, resp)
        suite = None
        if isinstance(resp, list):
            if "code" in resp[0]:
                logger.error("Fail to create SubTestSuite '%s' on '%s(ID:%s)'", suitename, self.__name, self.__id)
            else:
                logger.debug("Create SubTestSuite '%s' on TestSuite '%s(ID:%s)' Done", suitename, self.__name, self.__id)
                suite = TestSuite(self.server, self.devKey, resp[0]["id"], suitename, self.__projectid)
        elif isinstance(resp, dict):
            logger.error("SubTestSuite '%s' already exists on TestSuite '%s(ID:%s)'", suitename, self.__name, self.__id)
        else:
            pass
        return suite

    def createTestCase(self, name, summary="", steps="", preconditions=""):
        summary = '%s--Automatic create' % summary
        params = {  "devKey": self.devKey,
                    "testcasename": name,
                    "testsuiteid": self.__id,
                    "testprojectid": self.__projectid,
                    "authorlogin": "admin",
                    "summary": summary,
                    "steps": steps,
                    "preconditions": preconditions,
                    "execution_type": "TESTCASE_EXECUTION_TYPE_AUTO"
                }
        resp = self.server.tl.createTestCase(params)
        """
        [{'status': True, 'operation': 'createTestCase', 'id': '87135', 'message': 'Success!', 'additionalInfo': {'version_number': 1, 'new_name': '', 'id': '87135', 'tcversion_id': '87136', 'status_ok': 1, 'external_id': '9', 'msg': 'ok', 'has_duplicate': False}}]
        """
        logger.debug("Call TestLink API: createTestCase(%s), Response: %s", params, resp)
        case = None
        if "code" in resp[0]:
            logger.error("Fail to create TestCase '%s' on TestSuite '%s(ID:%s)'", name, self.__name, self.__id)
        else:
            case = TestCase(self.server, self.devKey, resp[0]["id"], name)
            logger.debug("Create TestCase '%s(ID:%s)' on TestSuite '%s(ID:%s)' Done", case.getName(), case.getId(), self.__name, self.__id)
        return case
    
    def getTestCases(self, deep=False, details="simple"):
        params = {"devKey": self.devKey, "testsuiteid": self.__id, "deep": deep, "details": details}
        resp = self.server.tl.getTestCasesForTestSuite(params)
        """
        full:   [{'node_order': '0', 'id': '87226', 'preconditions': 'Test Case Precondition', 'execution_type': '1', 'creation_ts': '2013-12-12 00:01:43', 'summary': 'Test Case Summary--Automatic create', 'layout': '1', 'external_id': 'test-44', 'steps': '', 'status': '1', 'tc_external_id': '44', 'updater_id': '', 'name': 'Test case', 'parent_id': '87225', 'tsuite_name': 'Test Suite', 'node_type_id': '3', 'author_id': '1', 'tcversion_id': '87227', 'node_table': 'testcases', 'active': '1', 'is_open': '1', 'importance': '2', 'version': '1', 'modification_ts': '0000-00-00 00:00:00'}, ]
        simple: [{'parent_id': '87225', 'node_order': '0', 'name': 'Test case', 'node_type_id': '3', 'node_table': 'testcases', 'id': '87226'}
        """
        logger.debug("Call TestLink API: getTestCasesForTestSuite(%s), Response: %s", params, resp)
        cases = []
        if not resp :
            logger.debug("No TestCases in TestSuite '%s(ID:%s)'", self.__name, self.__id)
        else:
            for tlCase in resp:
                case = TestCase(self.server, self.devKey, tlCase["id"], tlCase["name"])
                cases.append(case)
        return cases

    def getTestCasesByName(self, casename, deep=False):
        cases = []
        for case in self.getTestCases(deep):
            if case.getName() == casename:
                cases.append(case)
        return cases
    
    def getSubTestSuiteByName(self, suitename):
        retSubSuite = None
        for subSuite in self.getSubTestSuites():
            if subSuite.getName() == suitename:
                retSubSuite = subSuite
        return retSubSuite
        
    def getSubTestSuites(self):
        params = {"devKey":self.devKey, "testsuiteid":self.__id}
        resp = self.server.tl.getTestSuitesForTestSuite(params)
        """
        multi sub test suites:
        {
        '87131': {'node_order': '0', 'name': 'Test111', 'node_type_id': '2', 'details': '', 'id': '87131', 'parent_id': '87130'}, 
        '87132': {'node_order': '1', 'name': 'Test222', 'node_type_id': '2', 'details': '', 'id': '87132', 'parent_id': '87130'}
        }
        only on sub test suite:
        {'node_order': '0', 'node_type_id': '2', 'details': '<p>Create by ywu in YWU-P11LXX6</p>', 'id': '36035', 'name': 'IPAD', 'parent_id': '36034'}
        
        [{'code': 8000, 'message': '(getTestSuitesForTestSuite) - ID 8713011 do not belongs to a Test Suite present on system!'}]
        """
        logger.debug("Call TestLink API: getTestSuitesForTestSuite(%s), Response: %s", params, resp)
        suites = []
        if not resp:
            logger.debug("No SubTestSuites in TestSuite '%s(ID:%s)'", self.__name, self.__id)
        else:
            if isinstance(resp, dict):
                if "id" in resp:
                    suites.append(TestSuite(self.server, self.devKey, resp["id"], resp["name"], self.__projectid))
                else:
                    for tlSuite in list(resp.values()):
                        suites.append(TestSuite(self.server, self.devKey, tlSuite["id"], tlSuite["name"], self.__projectid))
            else:
                logger.error("Get TestSuites Error: %s", resp)
        return suites


class TestCase(object):
    def __init__(self, srvProxy, devKey, caseid, casename=""):
        self.server = srvProxy
        self.devKey = devKey
        self.__id   = caseid
        self.__name = casename
        self.__data = {}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<TestCase '%s(ID:%s)'>" % (self.__name, self.__id)

    def getId(self):
        return self.__id
    
    def getName(self):
        if not self.__name:
            self.__name = self.__getValue("name")
        return self.__name
    
    def __getValue(self, key):
        if not self.__data:
            params = {"devKey":self.devKey, "testcaseid": self.__id}
            resp = self.server.tl.getTestCase(params)
            """
            [{'author_last_name': 'Administrator', 'updater_last_name': '', 'preconditions': '', 'summary': '--Automatic create', 'testsuite_id': '87111', 'updater_first_name': '', 'steps': '', 'modification_ts': '0000-00-00 00:00:00', 'creation_ts': '2013-12-09 21:23:55', 'author_id': '1', 'author_login': 'admin', 'author_first_name': 'Testlink', 'status': '1', 'is_open': '1', 'version': '1', 'tc_external_id': '1', 'execution_type': '1', 'id': '87113', 'testcase_id': '87112', 'layout': '1', 'updater_login': '', 'name': 'Source Side Reset', 'importance': '2', 'node_order': '0', 'full_tc_external_id': 'test-1', 'updater_id': '', 'active': '1'}]
            [{'message': '(getTestCase) - The Test Case ID (testcaseid: 12314) provided does not exist!', 'code': 5000}]
            """
            logger.debug("Call TestLink API: getTestCase(%s), Response: %s", params, resp)
            if "code" in resp[0]:
                logger.error("Can't find TestCase 'ID:%s'", self.__name, self.__id)
            else:
                self.__data = resp[0]
        return self.__data[key]
    
    def getFullExtId(self):
        return self.__getValue("full_tc_external_id")

    def getVersion(self):
        return self.__getValue("version")


class TestPlan(object):
    def __init__(self, srvProxy, devKey, planid, planname, projectid):
        self.server = srvProxy
        self.devKey = devKey
        self.__id = planid
        self.__name = planname
        self.__projectid = projectid
        self.__data = {}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<TestPlan '%s(ID:%s)'>" % (self.__name, self.__id)
    
    def getName(self):
        return self.__name
    
    def getId(self):
        return self.__id
        
    def addTestSuite(self, objTestSuite):
        """Add TestCases(include SubTestSuite's TestCases) from the TestSuite object into TestPlan"""
        for objTestCase in objTestSuite.getTestCases():
            self.addTestCase(objTestCase)        
        for objSubTestSuite in objTestSuite.getSubTestSuites():
            self.addTestSuite(objSubTestSuite)
    
    def addTestCase(self, objTestCase):
        try:
            params = {"devKey": self.devKey,
                      "testplanid": self.__id,
                      "testprojectid": self.__projectid, 
                      "version": int(objTestCase.getVersion()),
                      "testcaseexternalid": objTestCase.getFullExtId()
                    }
            resp = self.server.tl.addTestCaseToTestPlan(params)
            logger.debug("Call TestLink API: addTestCaseToTestPlan(%s), Response: %s", params, resp)
            logger.debug("Add TestCase '%s(ID:%s)' into TestPlan '%s(ID:%s)' Done", objTestCase.getName(), objTestCase.getId(), self.__name, self.__id)
        except:
            logger.error("Already exists??? Fail to add TestCase '%s(ID:%s)' into TestPlan '%s(ID:%s)'", objTestCase.getName(), objTestCase.getId(), self.__name, self.__id)
    
    def getTestCases(self):
        params = {"devKey":self.devKey, "testplanid":self.__id}
        resp = self.server.tl.getTestCasesForTestPlan(params)
        """
        {
        '87114': [{'execution_type': '1', 'platform_id': '0', 'tcase_id': '87114', 'external_id': '2', 'execution_order': '1', 'tcversion_id': '87115', 'feature_id': '20924', 'platform_name': '', 'exec_status': 'p', 'tc_id': '87114', 'full_external_id': 'test-2', 'version': '1'}], 
        '87116': [{'execution_type': '1', 'platform_id': '0', 'tcase_id': '87116', 'external_id': '3', 'execution_order': '1', 'tcversion_id': '87117', 'feature_id': '20925', 'platform_name': '', 'exec_status': 'p', 'tc_id': '87116', 'full_external_id': 'test-3', 'version': '1'}], 
        }
        [{'message': '(getTestCasesForTestPlan) - The Test Plan ID (871091) provided does not exist!', 'code': 3000}]
        [{'code': 3032, 'message': 'Build (id:3241), does not exist for Test Plan (name:TestReport2TL/id:87109).'}]
        """
        logger.debug("Call TestLink API: getTestCasesForTestPlan(%s), Response: %s", params, resp)
        cases = []
        if not resp:
            logger.debug("No TestCases in Plan '%s(ID:%s)'", self.__name, self.__id)
        else:
            if isinstance(resp, dict):
                for caseid in resp.keys():
                    case = TestCase(self.server, self.devKey, caseid)
                    cases.append(case)
            elif isinstance(resp, list):
                logger.error("Can't find the TestCases: %s", resp)
            else:
                pass
        return cases

    def getTestSuites(self):
        params = {"devKey":self.devKey, "testplanid":self.__id}
        resp = self.server.tl.getTestSuitesForTestPlan(params)
        """
        [{'name': 'Manual Connection Test Suite', 'id': '87124', 'parent_id': '14979'}, {'name': 'Reset Test Suite', 'id': '87111', 'parent_id': '14979'}]
        [{'message': '(getTestSuitesForTestPlan) - The Test Plan ID (871019) provided does not exist!', 'code': 3000}]
        """
        logger.debug("Call TestLink API: getTestSuitesForTestPlan(%s), Response: %s", params, resp)
        suites = []
        if not resp:
            pass
        else:
            if "code" in resp[0]:
                logger.error("Get TestSuites on Plan '%s(ID:%s)' Fail", self.__name, self.__id)
            else:
                for tlSuite in resp:
                    suites.append(TestSuite(self.server, self.devKey, tlSuite["id"], tlSuite["name"], self.__projectid))
        return suites

    def getTestSuiteByName(self, suitename):
        retsuite = None
        for suite in self.getTestSuites():
            if suite.getName() == suitename:
                retsuite = suite
        return retsuite

    class Build(object):
        def __init__(self, data):
            self.__data = data
            self.__id   = self.__data["id"]
            self.__name = self.__data["name"]
    
        def __str__(self):
            return self.__repr__()

        def __repr__(self):
            return "<Build '%s(ID:%s)'>" % (self.__name, self.__id)

        def getId(self):
            return self.__id

        def getName(self):
            return self.__name

    def __TODO_getLatestBuild(self):
        pass
    
    def getBuilds(self):
        params = {"devKey": self.devKey, "testplanid": self.__id}
        resp = self.server.tl.getBuildsForTestPlan(params)
        """
        [
        {'testplan_id': '87109', 'release_date': '', 'active': '1', 'notes': 'Create by yyang3 in SH-EA05446626', 'id': '321', 'closed_on_date': '', 'name': 'SVN12345', 'is_open': '1'}, 
        {'testplan_id': '87109', 'release_date': '', 'active': '1', 'notes': 'Create by yyang3 in SH-EA05446626', 'id': '322', 'closed_on_date': '', 'name': 'SVN48660', 'is_open': '1'}, 
        ]
        """
        logger.debug("Call TestLink API: getBuildsForTestPlan(%s), Response: %s", params, resp)
        builds = []
        if not resp:
            logger.debug("No Builds in TestPlan '%s(ID:%s)'", self.__name, self.__id)
        else:
            if "code" in resp[0]:
                logger.error("Can't find Builds in TestPlan '%s(ID:%s)'", self.__name, self.__id)
            else:
                for tlBuild in resp:
                    builds.append(TestPlan.Build(tlBuild))
        return builds
    
    def getBuildByName(self, buildname):
        retBuild = None
        builds = self.getBuilds()
        for build in builds:
            if build.getName() == buildname:
                logger.debug("Found the Build '%s(ID:%s)' on TestPlan '%s(ID:%s)'", build.getName(), build.getId(), self.__name, self.__id )
                retBuild = build
        return retBuild
    
    def createBuild(self, buildname):
        buildnotes = 'Create by %s in %s' % (os.getenv('USERNAME'), os.getenv('COMPUTERNAME'))
        params = {"devKey": self.devKey, "testplanid": self.__id, "buildname": buildname, "buildnotes": buildnotes}
        resp = self.server.tl.createBuild(params)
        """
        [{'message': 'Success!', 'id': '333', 'operation': 'createBuild', 'status': True}]
        [{'message': 'Build name (SVN11111) already exists (id:331)', 'operation': 'createBuild', 'status': False, 'id': 331}]
        """
        logger.debug("Call TestLink API: createBuild(%s), Response: %s", params, resp)
        build = None
        if resp[0]["status"] == True:
            logger.debug("Create Build '%s' on TestPlan '%s(ID:%s)' Done", buildname, self.__name, self.__id)
            build = self.getBuildByName(buildname)
        else:
            logger.error("Build '%s' already exists on TestPlan '%s(ID:%s)'", buildname, self.__name, self.__id)
        return build

    def createTestExecution(self, buildname):
        objBuild = self.getBuildByName(buildname)
        if objBuild is None:
            objBuild = self.createBuild(buildname)
        return TestExecution(self.server, self.devKey, self, objBuild)


class TestExecution(object):
    def __init__(self, srvProxy, devkey, objPlan, objBuild):
        self.server = srvProxy
        self.devKey = devkey
        self.__objPlan = objPlan
        self.__objBuild = objBuild

    def setCaseExecResult(self, objCase, notes, status):
        notes = "%s Executed by %s in %s"  % (notes, os.getenv('USERNAME'), os.getenv('COMPUTERNAME'))
        params = {"devKey": self.devKey,
                  "testcaseid": objCase.getId(),
                  "testplanid": self.__objPlan.getId(),
                  "status": status,
                  "buildid": self.__objBuild.getId(),
                  "notes": notes,
                  "overwrite": True
                }
        resp = self.server.tl.reportTCResult(params)
        logger.debug("Call TestLink API: reportTCResult(%s), Response: %s", params, resp)

    def getCaseExecResult(self, objCase):
        params = {"devKey": self.devKey,
                  "testplanid": self.__objPlan.getId(),
                  "testcaseid": objCase.getId()
                }
        resp = self.server.tl.getLastExecutionResult(params)
        """[{'build_id': '391', 'status': 'f', 'tcversion_id': '33427', 'notes': '', 'tcversion_number': '1', 'testplan_id': '96059', 'execution_type': '1', 'platform_id': '0', 'execution_ts': '2014-02-10 22:45:55', 'tester_id': '28', 'id': '107497'}]"""
        logger.debug("Call TestLink API: getLastExecutionResult(%s), Response: %s", params, resp)
        if resp[0]["id"] == -1:
            return None
        else:
            return resp[0]
        

class TestLinkClient(object):      
    def __init__(self, srvUrl, devKey):
        self.server = ServerProxy(srvUrl, verbose=False)
        self.devKey = devKey

    def getTestProjectByName(self, name):
        params = {"devKey":self.devKey}
        resp = self.server.tl.getProjects(params)
        """
        [{'color': '', 'issue_tracker_enabled': '0', 'reqmgr_integration_enabled': '0', 'opt': {'testPriorityEnabled': 0, 'requirementsEnabled': 0, 'automationEnabled': 1, 'inventoryEnabled': 0}, 'options': 'O:8:"stdClass":4:{s:19:"requirementsEnabled";i:0;s:19:"testPriorityEnabled";i:0;s:17:"automationEnabled";i:1;s:16:"inventoryEnabled";i:0;}', 'active': '1', 'id': '38318', 'option_automation': '0', 'option_reqs': '0', 'option_priority': '0', 'notes': '<p>B&amp;A Linux driver, firmware and appliation test.</p>', 'prefix': 'BA', 'is_public': '1', 'tc_counter': '7901', 'name': 'B&A'}, 
        {'color': '', 'issue_tracker_enabled': '0', 'reqmgr_integration_enabled': '0', 'opt': {'testPriorityEnabled': 0, 'requirementsEnabled': 0, 'automationEnabled': 1, 'inventoryEnabled': 0}, 'options': 'O:8:"stdClass":4:{s:19:"requirementsEnabled";i:0;s:19:"testPriorityEnabled";i:0;s:17:"automationEnabled";i:1;s:16:"inventoryEnabled";i:0;}', 'active': '1', 'id': '81656', 'option_automation': '0', 'option_reqs': '0', 'option_priority': '0', 'notes': '<p>\n\tFor Test only</p>', 'prefix': 'Gen3', 'is_public': '1', 'tc_counter': '0', 'name': 'Gen3_Test'}, 
        ]
        [{'message': 'Can not authenticate client: invalid developer key', 'code': 2000}]
        """
        logger.debug("Call TestLink API: getProjects(%s), Response: %s", params, resp)
        project = None
        if not resp:
            logger.error("No any projects in the Server")
        else:
            for tlProject in resp:
                if tlProject['name'] == name:
                    project = TestProject(self.server, self.devKey, tlProject)
                    logger.debug("Found TestProject '%s(ID:%s)'", project.getName(), project.getId() )
            if project is None:
                logger.error("Can't find the project: %s", name)
        return project

    def impSuiteAndCases(self, projectName, structs, planName=""):
        """
        @param structs: The suites and cases you want to import, below is a sample 
        [
            {
                "name": "suitename", 
                "cases":[ {"name": "casename", "summary":"summary", "steps": "steps"}, ...],
                "subsuites": [ ... ]
            },
            { ... },
            { ... }
        ]
        @param planName: Optional. 
        If provide param 'planName', the suites and cases you provide in param 'structs' will also add into the plan. 
        The plan will be auto created if not exists.
        """
        logger.info("#" * 66)
        logger.info("# Start to import test suites and cases into TestLink.")
        logger.info("#" * 66)
        objProject = self.getTestProjectByName(projectName)
        if not objProject:
            return False
        
        if planName:
            objPlan = objProject.createTestPlan(planName)
        
        def recur(parent, struct):
            suiteName = struct["name"]
            objSuite = None
            if isinstance(parent, TestProject):
                objSuite = parent.createTopLevelTestSuite(suiteName)
            elif isinstance(parent, TestSuite):
                objSuite = parent.createSubTestSuite(suiteName)
            else:
                raise
            objCases = objSuite.getTestCases()
            
            oldCaseNames = map(lambda x: x.getName(), objCases)
            newCases = struct["cases"]
            for newCase in newCases:
                if newCase["name"] not in oldCaseNames:
                    logger.debug("TestCase '%s' not exist in TestSuite '%s(ID:%s)', create it.", newCase["name"], objSuite.getName(), objSuite.getId())
                    objSuite.createTestCase(**newCase)
                else:
                    logger.debug("TestCase '%s' already exist in TestSuite '%s(ID:%s)'", newCase["name"], objSuite.getName(), objSuite.getId())
                    
            if planName:
                objPlan.addTestSuite(objSuite)
            
            for subStruct in struct["subsuites"]:
                recur(objSuite, subStruct)
        
        for struct in structs:
            recur(objProject, struct)
        
        logger.info("#" * 66)
        logger.info("# Finish importing test suites and cases into TestLink.")
        logger.info("#" * 66)
        
        return True
        
    
if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )