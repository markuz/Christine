#!/usr/bin/env python
#
# Tests for the christienConf module
#

from libchristine.christineConf import christineConf
import unittest

class cconf(unittest.TestCase):

    def setUp(self):
        self.christineConf = christineConf()
        self.__testNotified = ''

    def testResetFile(self):
        self.christineConf.resetDefaults()
        self.assertEqual(1,1)

    def testErrorKey(self):
        key = '1/2/3'
        value = '123'
        self.assertRaises(KeyError,self.christineConf.setValue,key, value)

    def testSetNewOption(self):
        key = 'backend/2'
        value = '123'
        self.christineConf.setValue(key, value)
        s = self.christineConf.get(key)
        self.assertEqual(s,value)

    def testChangeValue(self):
        key = 'backend/audiosink'
        value = 'asfasfadfa'
        self.christineConf.setValue(key, value)
        self.assertEqual(value,self.christineConf.get(key))

    def testChangeBool(self):
        key = 'ui/show_pynotify'
        value = False
        self.christineConf.setValue(key, value)
        self.assertEqual(value,self.christineConf.getBool(key))

    def testIntBool(self):
        key = 'ui/show_pynotify'
        for i in range(1000):
            value = i
            self.christineConf.setValue(key, value)
            self.assertEqual(value,self.christineConf.getInt(key))

    def testFloatBool(self):
        key = 'ui/show_pynotify'
        for i in range(1000):
            value = i/0.5
            self.christineConf.setValue(key, value)
            self.assertEqual(value,self.christineConf.getFloat(key))

    def testNotifyAdd(self):
        key = 'backend/audiosink'
        self.christineConf.notifyAdd(key , self.__testNotify)
        self.christineConf.setValue(key, 'alsasink')
        self.assertEqual(self.__testNotified,self.christineConf.get(key))

    def __testNotify(self, value):
        self.__testNotified = value


