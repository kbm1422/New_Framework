#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import collections
"""
<TestReport>
    <Summary></Summary>
    <Comment></Comment>
    <ConfigFile></ConfigFile>
    <OverallTime></OverallTime>
    <TestSuite>
        <Name>New WVAN name Test Suite (SUITE_1)</Name>
        <TotalTests></TotalTests>
        <Failures></Failures>
        <Warnings></Warnings>
        <Errors></Errors>
        <Summary>Total Tests:100. Passed:78. Failures:22. Warnings:0. Suite Fail Rate: 22.0%. Suite Warning Rate: 0.0%</Summary>
        <SINK1_SW_VERSION/>
        <SRC1_SW_VERSION/>
        <SSSERVER_SW_VERSION/>
        <RepeatedTestStatistics>
            <Name></Name>
            <TotalTests></TotalTests>
            <Failures></Failures>
            <Warnings></Warnings>
            <AverageStatistics>associa
            <FailRate></FailRate>te time</AverageStatistics>
            <AverageStatistics>connect time</AverageStatistics>
            <AverageStatistics>total time</AverageStatistics>
        </RepeatedTestStatistics>
        <Test>
            <Number></Number>
            <Name></Name>
            <Title></Title>
            <TestLog></TestLog>
            <UevnetLog></UevnetLog>
            <Comment></Comment>
            <Comment></Comment>
            <Comment></Comment>
            <Result></Result>
        </Test>
    </TestSuite>
</TestReport>
"""
import os
import re

import simg.io.text as Text
import simg.xml.transform
from simg.xml.dom import minidom


class TestReport(object):
    def __init__(self, records):
        self.results = {"1": "PASSED",
          "2": "WARNING",
          "3": "FAILED",
          "4": "SKIPED",
          "5": "ERRONEOUS"}
        self._suiteresults = []
        if not records:
            raise NameError

        for record in records:
            fail_count = 0
            warn_count = 0
            suiteresult = {"suitename": record.name, "testresults": []}
            if not record.subrecords:
                raise NameError
            name = ""
            index = 1
            #record.subrecords = sorted(record.subrecords,key = lambda x:x.name)
            for subrecord in record.subrecords:
                print subrecord.__dict__
                testresult = dict()
                testresult["title"] = subrecord.name + " #" + str(subrecord.cycleindex)
                testresult["name"] = subrecord.name
                if not name:
                    name = testresult["name"]
                if name == testresult["name"]:
                    index += 1
                else:
                    index = 1
                testresult["result"] = self.results[str(subrecord.status)]
                checkpoint_no = len(subrecord.checkpoints)
                format_comments = [] # following code is for format the comments list, for eaxmple [{"CheckPoint":('123 should in 1234', 1),]
                if checkpoint_no:
                    for i in range (0, checkpoint_no):
                        _checkpoint_dict = {}
                        _checkpoint_dict["CheckPoint"] = subrecord.checkpoints[i]
                        format_comments.append(_checkpoint_dict)
                else:
                    format_comments.append({"CheckPoint": None})
                #format_comments.append({}.fromkeys(("Error",),subrecord.error))
                testresult["comments"] = format_comments
                if testresult["result"] == "FAILED":
                    fail_count += 1
                elif testresult["result"] == "WARNING":
                    warn_count += 1
                else:
                    pass
                suiteresult["testresults"].append(testresult)
            self._suiteresults.append(suiteresult)
                     
        
    def genXMLReport(self, dstFilename):
        self._dom = minidom.getDOMImplementation()
        self._doc = self._dom.createDocument(None, "TestReport", None)
        self._rootelement = self._doc.documentElement
        all_totaltests = 0
        all_failures = 0
        all_warnings = 0
        tests_number = 0
        for suiteresult in self._suiteresults:
            suite_totaltests = 0
            suite_failures = 0
            suite_warnings = 0
            suiteName = suiteresult["suitename"]
            suiteElement = self._rootelement.addSubElement("TestSuite")
            suiteElement.addSubElement("Name").addTextNode(suiteName)
            
            repeatedTestStatistics = collections.OrderedDict()
            for testresult in suiteresult["testresults"]:
                suite_totaltests += 1
                
                if testresult["name"] not in repeatedTestStatistics:
                    repeatedTestStatistics[testresult["name"]] = {"case_totaltests": 1,
                                                                  "statistics": collections.OrderedDict(),
                                                                  "case_failures": 0,
                                                                  "case_warnings": 0
                                                                  }
                else:
                    repeatedTestStatistics[testresult["name"]]["case_totaltests"] += 1
                
                testElement = suiteElement.addSubElement("Test")
                #match = re.search("(\d+)$", testresult["title"])
                #if match:
                #    number = match.group(1)
                tests_number += 1
                testElement.addSubElement("Number").addTextNode(str(tests_number))
                
                testElement.addSubElement("Title").addTextNode(testresult["title"])
                testElement.addSubElement("Name").addTextNode(testresult["name"])
                
                for comment in testresult["comments"]:
                    _comment_text = comment ["CheckPoint"]
                    if not _comment_text:
                        _comment_text = "CheckPort:None"
                    else:
                        _comment_text = "CheckPoint:" + comment["CheckPoint"][0] + " Result:" + self.results[str(comment["CheckPoint"][1])]
                    
                    testElement.addSubElement("Comment").addTextNode(_comment_text)
                
                if testresult["result"] == "FAILED":
                    suite_failures += 1
                    repeatedTestStatistics[testresult["name"]]["case_failures"] += 1
                elif testresult["result"] == "WARNING":
                    suite_warnings += 1
                    repeatedTestStatistics[testresult["name"]]["case_warnings"] += 1
                else:
                    pass
                
                testElement.addSubElement("Result").addTextNode(testresult["result"].upper())

            for key, value in repeatedTestStatistics.items():
                if value["case_totaltests"] == 1:
                    continue
                statisticsElement = suiteElement.addSubElement("RepeatedTestStatistics")
                statisticsElement.addSubElement("Name").addTextNode(key)
                statisticsElement.addSubElement("TotalTests").addTextNode(str(value["case_totaltests"]))
                statisticsElement.addSubElement("Failures").addTextNode(str(value["case_failures"]))
                statisticsElement.addSubElement("Warnings").addTextNode(str(value["case_warnings"]))
            
                failrate = round(float(value["case_failures"]) / float(value["case_totaltests"]), 3) * 100
                statisticsElement.addSubElement("FailRate").addTextNode(str(failrate) + "%")
                
                for stakey, stavalue in repeatedTestStatistics[key]["statistics"].items():
                    if stavalue:
                        statisticsElement.addSubElement("AverageStatistics").addTextNode("%s: %s" % (stakey, sum(stavalue) / len(stavalue)))
                
            
            suiteElement.addSubElement("TotalTests").addTextNode(str(suite_totaltests))
            suiteElement.addSubElement("Failures").addTextNode(str(suite_failures))
            suiteElement.addSubElement("Warnings").addTextNode(str(suite_warnings))

            failrate = round(float(suite_failures) / float(suite_totaltests), 3) * 100
            warnrate = round(float(suite_warnings) / float(suite_totaltests), 3) * 100
            summary = "Total Tests:%s. Failures:%s. Warnings:%s. Fail Rate: %s%%. Warning Rate: %s%%" % (suite_totaltests, suite_failures, suite_warnings, failrate, warnrate)
            suiteElement.addSubElement("Summary").addTextNode(summary)
            
            all_totaltests += suite_totaltests
            all_failures += suite_failures
            all_warnings += suite_warnings

        failrate = round(float(all_failures) / float(all_totaltests), 3) * 100
        warnrate = round(float(all_warnings) / float(all_totaltests), 3) * 100
        summary = "Total Tests:%s. Failures:%s. Warnings:%s. Suite Fail Rate: %s%%. Suite Warning Rate: %s%%" % (all_totaltests, all_failures, all_warnings, failrate, warnrate)            
        self._rootelement.addSubElement("Summary").addTextNode(summary)

        
        with open(dstFilename, "w") as fdst:
            fdst.write(self._doc.toprettyxml())
    

    def genHTMLReport(self, srcFilename, dstFilename):
        dirname = os.path.dirname(__file__)
        transformer = simg.xml.transform.TransformerFactory.netTransformer(os.path.join(dirname, "report.xsl"))
        transformer.applyStylesheetOnFile(srcFilename)
        transformer.saveResultToFilename(dstFilename)
        pass


class BADriverTestReport(object):    
    def __init__(self):
        self._suiteresults = []
        self._txteditor = Text.TextEditor()
        self._statisticsCommentPrefixes = {
            "B&A driver off to mhl mode test": ["mode change from mhl to off", "mode change from off to mhl"],
            "B&A driver off to wihd mode test": ["mode change from wihd to off", "mode change from off to wihd"],
            "B&A driver associated to off mode test": ["mode change from wihd associated to off"],
            "B&A driver associated to mhl mode test": ["mode change from wihd associated to mhl"],
            "B&A driver connected to mhl mode test": ["associate duration time", "connect duration time"],
            "B&A driver connected to off mode test": ["mode change from wihd connect to off"],
            "B&A driver wihd mode idle to mhl mode test": ["mode change from wihd idle to mhl", "mode change from mhl to wihd idle"],
            "B&A driver wvan_scan to off mode test": ["mode change from wihd scan to off"],
            "B&A driver wvan_scan to mhl mode test": ["mode change from wihd scan to mhl"],
            
            # TODO:
            "B&A driver interval scan from idle test": ["scan start uevent send out after command issued"],
            "B&A driver interval scan from scan test": [],
            "B&A driver scan from idle test": ["unit scan duration", "scan start uevent send out after command issued"],
            "B&A driver scan from scan test": [],
            "B&A driver scan stop test": [],
            
            # TODO:
            "B&A driver search between connect disconnect test": [],
            "B&A driver search from associated test": [],
            
            "B&A driver join from idle test": ["associate duration"],
            "B&A driver join from period scan test": [],

            "B&A driver connect/disconnect remote read test": ["connect duration time"],
            "B&A driver mac address connect/disassociate test": ["associate duration time", "connect duration time"],
            "B&A A1 driver mac address connect/disconnect test" : ["connect duration time"],
            "B&A driver mac address connect/disconnect and disassociate test": ["associate duration time", "connect duration time"],
            "B&A driver connected remote read test": ["connect duration time"],

            "B&A driver factory test": ["associate time", "temperature_a", "connect time", "temperature_b", "the time cost between fm_test_mode and connected", "hr link quality"],
            "B&A driver get associate and connect time test": ["associate time", "connect time"],
            "B&A driver get reconnect time test": ["reconnect time"],
        }
        
    def addLogForParsing(self, logfile, suitename):
        suiteExists = False
        suiteResult = {"suitename": suitename, "testresults": []}
        
        for result in self._suiteresults:
            if result["suitename"] == suitename:
                suiteExists = True
                suiteResult = result
                break

        fail_count = 0
        warn_count = 0
        
        self._txteditor.load(logfile)
        titlelines = self._txteditor.search(r"TEST_TITLE: ")

        for titleline in titlelines:
            testresult = {}
            match = re.search(r"TEST_TITLE: ((.*test).*)", titleline)
            testresult["title"] = match.group(1).strip()
            testresult["name"] = match.group(2).strip()

            resultlines = self._txteditor.search(r"%s_TEST_RESULT: " % testresult["title"])
            match = re.search(r"%s_TEST_RESULT: (.*)" % testresult["title"], resultlines[0])
            testresult["result"] = match.group(1).strip()
            
            if testresult["result"] == "failed":
                fail_count += 1
            elif testresult["result"] == "warning":
                warn_count += 1
            else:
                pass
            
            commentlines = self._txteditor.search(r"%s_TEST_COMMENT: " % testresult["title"])
            comments = []
            for commentline in commentlines:
                match = re.search(r"%s_TEST_COMMENT: (.*)\r?" % testresult["title"], commentline)
                comment = match.group(1)
                if comment[0] == "[" and comment[-1] == "]":
                    comms = eval(comment)
                    for comm in comms:
                        comments.append(str(comm))
                else:
                    comments.append(comment)
            testresult["comments"] = comments
            
            suiteResult["testresults"].append(testresult)

        if not suiteExists:
            self._suiteresults.append(suiteResult)

    
    def genXMLReport(self, dstFilename):
        self._dom = minidom.getDOMImplementation()
        self._doc = self._dom.createDocument(None, "TestReport", None)
        self._rootelement = self._doc.documentElement
        all_totaltests = 0
        all_failures = 0
        all_warnings = 0
        for suiteresult in self._suiteresults:
            suite_totaltests = 0
            suite_failures = 0
            suite_warnings = 0
            suiteName = suiteresult["suitename"]
            suiteElement = self._rootelement.addSubElement("TestSuite")
            suiteElement.addSubElement("Name").addTextNode(suiteName)
            
            repeatedTestStatistics = collections.OrderedDict()
            for testresult in suiteresult["testresults"]:
                suite_totaltests += 1
                
                if testresult["name"] not in repeatedTestStatistics:
                    repeatedTestStatistics[testresult["name"]] = {"case_totaltests": 1,
                                                                  "statistics": collections.OrderedDict(),
                                                                  "case_failures": 0,
                                                                  "case_warnings": 0
                                                                  }
                else:
                    repeatedTestStatistics[testresult["name"]]["case_totaltests"] += 1
                
                testElement = suiteElement.addSubElement("Test")
                match = re.search("(\d+)$", testresult["title"])
                if match:
                    number = match.group(1)
                    testElement.addSubElement("Number").addTextNode(number)
                
                testElement.addSubElement("Title").addTextNode(testresult["title"])
                testElement.addSubElement("Name").addTextNode(testresult["name"])
                
                for comment in testresult["comments"]:
                    testElement.addSubElement("Comment").addTextNode(comment)
                    if testresult["name"] in self._statisticsCommentPrefixes:
                        filtercomments = self._statisticsCommentPrefixes[testresult["name"]]
                    else:
                        filtercomments = []
                    if testresult["result"] != "failed" and filter(lambda x: x in comment, filtercomments):
                        if "issued" in comment:
                            if "[" in comment and "]" in comment:
                                match = re.search(r"(.* issued) (\[[\.\d,]+\])s", comment)
                                name = match.group(1)
                                values = eval(match.group(2))
                                value = sum(values) / len(values)
                            else:
                                match = re.search(r"(.* issued) ([\.\d]+)", comment)
                                name = match.group(1)
                                value = match.group(2)
                        else:
                            match = re.search(r"(.*)(?: is|[ ]?:) ([\.\d]+)", comment)
                            name = match.group(1)
                            value = match.group(2)
                        if name in repeatedTestStatistics[testresult["name"]]["statistics"]:
                            repeatedTestStatistics[testresult["name"]]["statistics"][name].append(float(value))
                        else:
                            repeatedTestStatistics[testresult["name"]]["statistics"][name] = list()
                
                if testresult["result"] == "failed":
                    suite_failures += 1
                    repeatedTestStatistics[testresult["name"]]["case_failures"] += 1
                elif testresult["result"] == "warning":
                    suite_warnings += 1
                    repeatedTestStatistics[testresult["name"]]["case_warnings"] += 1
                else:
                    pass
                
                testElement.addSubElement("Result").addTextNode(testresult["result"].upper())

            for key, value in repeatedTestStatistics.items():
                if value["case_totaltests"] == 1:
                    continue
                statisticsElement = suiteElement.addSubElement("RepeatedTestStatistics")
                statisticsElement.addSubElement("Name").addTextNode(key)
                statisticsElement.addSubElement("TotalTests").addTextNode(str(value["case_totaltests"]))
                statisticsElement.addSubElement("Failures").addTextNode(str(value["case_failures"]))
                statisticsElement.addSubElement("Warnings").addTextNode(str(value["case_warnings"]))
            
                failrate = round(float(value["case_failures"]) / float(value["case_totaltests"]), 3) * 100
                statisticsElement.addSubElement("FailRate").addTextNode(str(failrate) + "%")
                
                for stakey, stavalue in repeatedTestStatistics[key]["statistics"].items():
                    if stavalue:
                        statisticsElement.addSubElement("AverageStatistics").addTextNode("%s: %s" % (stakey, sum(stavalue) / len(stavalue)))
                
            
            suiteElement.addSubElement("TotalTests").addTextNode(str(suite_totaltests))
            suiteElement.addSubElement("Failures").addTextNode(str(suite_failures))
            suiteElement.addSubElement("Warnings").addTextNode(str(suite_warnings))

            failrate = round(float(suite_failures) / float(suite_totaltests), 3) * 100
            warnrate = round(float(suite_warnings) / float(suite_totaltests), 3) * 100
            summary = "Total Tests:%s. Failures:%s. Warnings:%s. Fail Rate: %s%%. Warning Rate: %s%%" % (suite_totaltests, suite_failures, suite_warnings, failrate, warnrate)
            suiteElement.addSubElement("Summary").addTextNode(summary)
            
            all_totaltests += suite_totaltests
            all_failures += suite_failures
            all_warnings += suite_warnings

        failrate = round(float(all_failures) / float(all_totaltests), 3) * 100
        warnrate = round(float(all_warnings) / float(all_totaltests), 3) * 100
        summary = "Total Tests:%s. Failures:%s. Warnings:%s. Suite Fail Rate: %s%%. Suite Warning Rate: %s%%" % (all_totaltests, all_failures, all_warnings, failrate, warnrate)            
        self._rootelement.addSubElement("Summary").addTextNode(summary)

        
        with open(dstFilename, "w") as fdst:
            fdst.write(self._doc.toprettyxml())
    

    def genHTMLReport(self, srcFilename, dstFilename):
        dirname = os.path.dirname(__file__)
        transformer = simg.xml.transform.TransformerFactory.netTransformer(os.path.join(dirname, "report.xsl"))
        transformer.applyStylesheetOnFile(srcFilename)
        transformer.saveResultToFilename(dstFilename)

    
if __name__ == "__main__":
    tr = BADriverTestReport()
#     tr.addLogForParsing(r"W:\SQA\TestReports\B&A\Android\SVN49318\2014-01-13_17-49-12\factory.log", "factory")
#     tr.addLogForParsing(r"Y:\logs\2014-01-20_09-40-46\flash_sink_fw.log", "ota")
    
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\install.log", "install")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\reinstall.log", "reinstall")
 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\idle_to_mhl.log", "mode")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\off_to_mhl.log", "mode")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\off_to_wihd.log", "mode")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connected_to_mhl.log", "mode")    
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connected_to_off.log", "mode") 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\associated_to_off.log", "mode")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\associated_to_mhl.log", "mode")
 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\intervscan_from_idle.log", "scan")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\intervscan_from_scan.log", "scan")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\scan_from_idle.log", "scan")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\scan_from_scan.log", "scan")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\scan_stop.log", "scan")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\scan_to_mhl.log", "scan")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\scan_to_off.log", "scan")
 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\search_between_connect_disconnect.log", "search")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\search_from_associated.log", "search") 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\search_from_connected.log", "search") 
 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\join_from_idle.log", "join")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\join_from_periodscan.log", "join") 
 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connect_disconnect_remote_read.log", "connect")
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connect_mac_disassoc.log", "connect")    
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connect_mac_disconnect_A1.log", "connect") 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connect_mac_disconnect_disassoc.log", "connect") 
    tr.addLogForParsing(r"D:\2013-12-03_15-40-07\connected_remote_read.log", "connect")


    tr.genXMLReport("d:/testreport.xml")
    tr.genHTMLReport("d:/testreport.xml", "d:/testreport.html")



