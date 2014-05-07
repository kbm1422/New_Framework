#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from com.android.monkeyrunner.easy import EasyMonkeyDevice
from com.android.monkeyrunner.easy import By
from com.android.chimpchat.hierarchyviewer import HierarchyViewer


class Application(object):
    def __init__(self, device, viewer, package):
        self._device = device
        self._viewer = viewer
        self.package = package
    
    def start(self, activity=None):
        activity = activity or ".MainActivity"
        runComponent = self.package + "/" + activity
        self._device.startActivity(component=runComponent)
    
    def install(self, apk):
        self._device.installPackage(apk)
    
    def uninstall(self):
        self._device.removePackage(self.package)
    
    def getViewById(self, uid):
        viewnode = self._viewer.findViewById(uid)
        if viewnode is None:
            return None

        if viewnode.name == "android.widget.TextView":
            cls = TextView
        elif viewnode.name == "android.widget.Button":
            cls = Button
        elif viewnode.name == "android.widget.EditText":
            cls = EditText            
        elif viewnode.name == "android.widget.Switch":
            cls = Switch  
        elif viewnode.name == "android.widget.SeekBar":
            cls = SeekBar  
        return cls(self._device, self._viewer, viewnode)


class View(object):
    def __init__(self, device, viewer, viewnode):
        self._device = device
        self._viewer = viewer
        self._id = id
        self.viewnode = viewnode

    def touch(self, ktype=MonkeyDevice.DOWN_AND_UP):
        coordinate = self._viewer.getAbsoluteCenterOfView(self.viewnode)
        self._device.touch(coordinate.x, coordinate.y, ktype)
        
    def isKeyboardShown(self):
        dim = self._device.shell('dumpsys input_method')
        if dim:
            return "mInputShown=true" in dim
        return False

    def closeKeyboard(self):
        if self.isKeyboardShown():
            self._device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)        


class Button(View):
    pass


class TextView(View):
    def getText(self):
        return self.viewnode.namedProperties.get("text:mText").value


class EditText(TextView):
    def delText(self):
        self.touch()
        text = self.getText()
        self._device.press('KEYCODE_MOVE_END', MonkeyDevice.DOWN_AND_UP)
        for _ in range(35):
            self._device.press('KEYCODE_DEL', MonkeyDevice.DOWN_AND_UP)
        self.closeKeyboard()
            
    def setText(self, text):
        self.delText()
        self._device.type(text)
        self.closeKeyboard()


class Switch(View):
    def isChecked(self):
        if self.viewnode.namedProperties.get("isChecked()").value == "true":
            return True
        else:
            return False

    def turnOn(self):
        if not self.isChecked():
            self.touch()
    
    def turnOff(self):
        if self.isChecked():
            self.touch()


class SeekBar(View):
    def getMaxProcess(self):
        return int(self.viewnode.namedProperties.get("progress:getMax()").value)
    
    def setProcess(self, number):
        startPosition = self._viewer.getAbsolutePositionOfView(self.viewnode)
        maxProcess = self.getMaxProcess()
        start = (startPosition.x, startPosition.y)
        interval = float(self.viewnode.width)/maxProcess
        end = (startPosition.x + int(interval*number)+int(interval/2), startPosition.y)
        self._device.drag(start, end)


class MonkeyRunnerClient():
    @classmethod
    def getApplication(cls, name):
        device = MonkeyRunner.waitForConnection()
        viewer = device.getHierarchyViewer()
        return Application(device, viewer, 'com.simg.WMDisplay')


if __name__ == "__main__":
    pass